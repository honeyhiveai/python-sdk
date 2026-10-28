from enum import Enum


class ChartQueryAggregation(str, Enum):
    COUNT = "count"

    AVG = "avg"

    SUM = "sum"

    MIN = "min"

    MAX = "max"

    MEDIAN = "median"

    P50 = "p50"

    P75 = "p75"

    P90 = "p90"

    P95 = "p95"

    P99 = "p99"

    PERCENTAGE_TRUE = "percentage_true"

    PERCENTAGE_FALSE = "percentage_false"

    PERCENTAGE_NULL = "percentage_null"
