"""
FermentIQ Anomaly Engine
Pure Python/NumPy signal comparison engine.
No third-party AI APIs used.
"""
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum


class TankStatus(Enum):
    PERFECT = "perfect"        # similarity >= 95%
    ACCEPTABLE = "acceptable"  # similarity >= 80%
    CONCERNING = "concerning"  # similarity >= 60%
    FAILED = "failed"          # similarity < 60%


@dataclass
class AnomalyResult:
    tank_id: str
    similarity_score: float          # 0.0 to 100.0
    status: TankStatus
    first_deviation_index: Optional[int]
    first_deviation_timestamp: Optional[str]
    deviation_details: List[dict]    # [{index, reading, ideal, delta, exceeded_tolerance}]


class FermentationAnomalyEngine:
    """
    Compares N tank readings against the ideal fermentation signature S
    using tolerance-band matching (not DTW, keeping it dependency-light).
    """

    def __init__(self, ideal_signature: List[float], tolerance_pct: float = 10.0):
        """
        ideal_signature: list of S float values (the perfect fermentation curve)
        tolerance_pct: allowed % deviation at each point (default 10%)
        """
        self.ideal = [float(x) for x in ideal_signature]
        self.tolerance_pct = tolerance_pct
        self.S = len(self.ideal)

    def _tolerance_band(self) -> Tuple[np.ndarray, np.ndarray]:
        margin = [abs(v) * (self.tolerance_pct / 100.0) for v in self.ideal]
        margin = [m if m >= 0.01 else 0.01 for m in margin]
        lower = [self.ideal[i] - margin[i] for i in range(self.S)]
        upper = [self.ideal[i] + margin[i] for i in range(self.S)]
        return lower, upper

    def analyze_tank(
        self,
        tank_id: str,
        readings: List[float],
        timestamps: Optional[List[str]] = None
    ) -> AnomalyResult:
        """
        Analyze one tank's readings against ideal signature.
        Readings are trimmed/padded to match S if needed.
        """
        readings_arr = [float(x) for x in readings[:self.S]]

        # Pad if shorter by repeating last value
        if len(readings_arr) < self.S:
            if len(readings_arr) == 0:
                readings_arr = [0.0] * self.S
            else:
                last = readings_arr[-1]
                readings_arr = readings_arr + [last] * (self.S - len(readings_arr))

        lower, upper = self._tolerance_band()

        in_band = [lower[i] <= readings_arr[i] <= upper[i] for i in range(self.S)]
        similarity_score = float(sum(1 for v in in_band if v) / self.S * 100.0)

        # Find first deviation
        deviation_indices = [i for i, v in enumerate(in_band) if not v]
        first_dev_index = int(deviation_indices[0]) if len(deviation_indices) > 0 else None
        first_dev_ts = None
        if first_dev_index is not None and timestamps is not None and first_dev_index < len(timestamps):
            first_dev_ts = timestamps[first_dev_index]

        # Build deviation details
        details = []
        for i in range(self.S):
            if not in_band[i]:
                details.append({
                    "index": i,
                    "reading": round(float(readings_arr[i]), 4),
                    "ideal": round(float(self.ideal[i]), 4),
                    "delta": round(float(readings_arr[i] - self.ideal[i]), 4),
                    "exceeded_tolerance": True
                })

        # Classify status
        if similarity_score >= 95:
            status = TankStatus.PERFECT
        elif similarity_score >= 80:
            status = TankStatus.ACCEPTABLE
        elif similarity_score >= 60:
            status = TankStatus.CONCERNING
        else:
            status = TankStatus.FAILED

        return AnomalyResult(
            tank_id=tank_id,
            similarity_score=round(similarity_score, 2),
            status=status,
            first_deviation_index=first_dev_index,
            first_deviation_timestamp=first_dev_ts,
            deviation_details=details
        )

    def analyze_all_tanks(self, tanks: dict, timestamps: Optional[List[str]] = None) -> List[AnomalyResult]:
        """tanks = {"tank_01": [readings...], "tank_02": [...]}"""
        return [self.analyze_tank(tid, readings, timestamps) for tid, readings in tanks.items()]


# ── Inline self-test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    ideal = [20.0 + i * 0.5 for i in range(50)]
    engine = FermentationAnomalyEngine(ideal_signature=ideal, tolerance_pct=10.0)

    # Perfect tank
    result = engine.analyze_tank("tank_perfect", ideal)
    assert result.status == TankStatus.PERFECT, f"Expected PERFECT, got {result.status}"
    assert result.similarity_score == 100.0

    # Failed tank (random noise)
    noisy = [v + 50 for v in ideal]
    result2 = engine.analyze_tank("tank_failed", noisy)
    assert result2.status == TankStatus.FAILED

    print("✅ AnomalyEngine self-tests passed.")
