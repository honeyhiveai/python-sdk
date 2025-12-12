from enum import Enum


class GetExperimentComparisonAggregateFunction(str, Enum):
    AVERAGE = "average"
    COUNT = "count"
    MAX = "max"
    MEDIAN = "median"
    MIN = "min"
    P90 = "p90"
    P95 = "p95"
    P99 = "p99"
    SUM = "sum"

    def __str__(self) -> str:
        return str(self.value)
