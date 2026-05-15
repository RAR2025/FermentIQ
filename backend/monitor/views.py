import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import IdealSignature, TankReading, AnalysisResult
from .serializers import IdealSignatureSerializer, TankReadingSerializer, AnalysisResultSerializer
from .simulator import FermentationSimulator
from .anomaly_engine import FermentationAnomalyEngine


class SimulateView(APIView):
    def get(self, request):
        try:
            sim = FermentationSimulator()
            ideals = sim.get_ideal_signatures()
            timestamps = sim.generate_timestamps()
            try:
                n_tanks = int(request.query_params.get('n_tanks', 6))
            except Exception:
                n_tanks = 6
            n_tanks = max(1, min(n_tanks, 24))

            fault_types = ["none", "none", "drift", "spike", "stuck", "random"]

            # Save ideals
            for sensor, values in ideals.items():
                IdealSignature.objects.create(sensor=sensor, values_json=json.dumps(values))

            # Generate tanks
            tanks = {}
            for i in range(n_tanks):
                tid = f"tank_{i+1:02d}"
                fault = fault_types[i % len(fault_types)]
                fault_start = 30 + (i * 3) % 20
                sensor_readings = {
                    sensor: sim.generate_tank_readings(ideals[sensor], fault, fault_start)
                    for sensor in ideals
                }
                tanks[tid] = sensor_readings
                for sensor, readings in sensor_readings.items():
                    TankReading.objects.create(
                        tank_id=tid,
                        sensor=sensor,
                        values_json=json.dumps(readings),
                        timestamps_json=json.dumps(timestamps),
                        fault_type=fault
                    )

            return Response({"ideals": ideals, "tanks": tanks, "timestamps": timestamps, "n_tanks": n_tanks})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalyzeView(APIView):
    def get(self, request):
        try:
            # Load latest ideal signatures
            ideals_qs = IdealSignature.objects.all().order_by('-created_at')
            ideals = {}
            for obj in ideals_qs:
                ideals[obj.sensor] = json.loads(obj.values_json)

            # Load latest tank readings grouped by tank
            tr_qs = TankReading.objects.all().order_by('-created_at')
            tanks = {}
            timestamps = None
            for tr in tr_qs:
                sensor_map = tanks.setdefault(tr.tank_id, {})
                if tr.sensor in sensor_map:
                    continue
                if timestamps is None:
                    try:
                        timestamps = json.loads(tr.timestamps_json)
                    except Exception:
                        timestamps = None
                sensor_map[tr.sensor] = json.loads(tr.values_json)

            results = []
            # For each tank and sensor, run analyzer
            for tid, sensors in tanks.items():
                for sensor, readings in sensors.items():
                    ideal = ideals.get(sensor)
                    if ideal is None:
                        continue
                    engine = FermentationAnomalyEngine(ideal_signature=ideal, tolerance_pct=10.0)
                    res = engine.analyze_tank(tid + ":" + sensor, readings, timestamps)
                    # Save AnalysisResult
                    AnalysisResult.objects.create(
                        tank_id=tid,
                        sensor=sensor,
                        similarity_score=res.similarity_score,
                        status=res.status.value,
                        first_deviation_index=res.first_deviation_index if res.first_deviation_index is not None else None,
                        first_deviation_timestamp=res.first_deviation_timestamp,
                        deviation_count=len(res.deviation_details)
                    )
                    results.append({
                        "tank_id": tid,
                        "sensor": sensor,
                        "similarity_score": res.similarity_score,
                        "status": res.status.value,
                        "first_deviation_index": res.first_deviation_index,
                        "first_deviation_timestamp": res.first_deviation_timestamp,
                        "deviation_details": res.deviation_details
                    })

            return Response({"analysis": results})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResultsView(APIView):
    def get(self, request):
        try:
            qs = AnalysisResult.objects.all().order_by('-analyzed_at')
            serializer = AnalysisResultSerializer(qs, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthView(APIView):
    def get(self, request):
        try:
            return Response({"status": "ok", "version": "1.0.0"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
