"""
FermentIQ Synthetic Data Simulator
Generates realistic fermentation sensor data for N tanks.
Sensors: temperature (°C), pH, dissolved_oxygen (%)
"""
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List


class FermentationSimulator:
    """
    Generates the ideal signature and per-tank readings
    with configurable noise and fault injection.
    """

    # Realistic fermentation curves (S=72 points = 72 hours)
    S = 72  # number of time points

    @staticmethod
    def ideal_temperature() -> List[float]:
        """Temperature rises then stabilizes: 18°C → 24°C → 22°C"""
        t = [i / (FermentationSimulator.S - 1) for i in range(FermentationSimulator.S)]
        curve = [18 + 6 * math.exp(-((tt - 0.3) ** 2) / 0.05) + random.gauss(0, 0.05) for tt in t]
        return curve

    @staticmethod
    def ideal_ph() -> List[float]:
        """pH drops from 6.5 to 4.2 during fermentation"""
        t = [i / (FermentationSimulator.S - 1) for i in range(FermentationSimulator.S)]
        curve = [6.5 - 2.3 * (1 - math.exp(-5 * tt)) + random.gauss(0, 0.02) for tt in t]
        return [min(7.0, max(3.5, v)) for v in curve]

    @staticmethod
    def ideal_dissolved_oxygen() -> List[float]:
        """DO drops rapidly as yeast consumes oxygen: 95% → 15%"""
        t = [i / (FermentationSimulator.S - 1) for i in range(FermentationSimulator.S)]
        curve = [95 * math.exp(-4 * tt) + 10 + random.gauss(0, 0.3) for tt in t]
        return [min(100.0, max(5.0, v)) for v in curve]

    def get_ideal_signatures(self) -> Dict[str, List[float]]:
        return {
            "temperature": self.ideal_temperature(),
            "ph": self.ideal_ph(),
            "dissolved_oxygen": self.ideal_dissolved_oxygen()
        }

    def generate_timestamps(self, start: datetime = None) -> List[str]:
        if start is None:
            start = datetime.now() - timedelta(hours=self.S)
        return [(start + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%S") for i in range(self.S)]

    def generate_tank_readings(
        self,
        ideal: List[float],
        fault_type: str = "none",   # "none", "spike", "drift", "stuck", "random"
        fault_start: int = 40
    ) -> List[float]:
        """
        Generate tank readings from ideal with optional fault injection.
        fault_type: type of failure to simulate
        fault_start: index where fault begins
        """
        readings = [float(x) for x in ideal]

        # Base natural noise (±2%)
        readings = [r + random.gauss(0, abs(r) * 0.02) for r in readings]

        if fault_type == "spike":
            for idx in range(fault_start, min(fault_start + 5, self.S)):
                readings[idx] += abs(readings[idx]) * 0.4

        elif fault_type == "drift":
            if fault_start < self.S:
                end = self.S
                total = end - fault_start
                base = abs(readings[fault_start]) * 0.35
                for i in range(total):
                    readings[fault_start + i] += (base * i / max(1, total - 1))

        elif fault_type == "stuck":
            if fault_start < self.S:
                val = readings[fault_start]
                for idx in range(fault_start, self.S):
                    readings[idx] = val

        elif fault_type == "random":
            if fault_start < self.S:
                for idx in range(fault_start, self.S):
                    readings[idx] += random.gauss(0, abs(readings[fault_start]) * 0.3)

        return readings

    def generate_all_tanks(self, n_tanks: int = 6) -> Dict[str, Dict[str, List[float]]]:
        """
        Returns {tank_id: {sensor: [readings]}} for n_tanks tanks.
        Distributes fault types across tanks for demo variety.
        """
        ideal_sigs = self.get_ideal_signatures()
        fault_types = ["none", "none", "drift", "spike", "stuck", "random"]
        tanks = {}

        for i in range(n_tanks):
            tid = f"tank_{i+1:02d}"
            fault = fault_types[i % len(fault_types)]
            fault_start = random.randint(30, 55)
            tanks[tid] = {
                sensor: self.generate_tank_readings(ideal_sigs[sensor], fault, fault_start)
                for sensor in ideal_sigs
            }

        return tanks


# ── Inline self-test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    sim = FermentationSimulator()
    ideals = sim.get_ideal_signatures()
    assert len(ideals["temperature"]) == 72
    assert len(ideals["ph"]) == 72
    tanks = sim.generate_all_tanks(4)
    assert len(tanks) == 4
    assert "tank_01" in tanks
    print("✅ Simulator self-tests passed.")
