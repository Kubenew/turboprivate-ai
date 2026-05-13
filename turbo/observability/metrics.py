from prometheus_client import Counter, Gauge, Histogram

LATENCY_BUCKETS = [0.01, 0.05, 0.1, 0.5, 1, 5]


class MetricsRegistry:
    def __init__(self):
        self.requests_total = Counter(
            "turbo_requests_total", "Total inference requests"
        )
        self.tokens_total = Counter(
            "turbo_tokens_total", "Total tokens generated"
        )
        self.latency = Histogram(
            "turbo_latency_seconds",
            "Request latency",
            buckets=LATENCY_BUCKETS,
        )
        self.gpu_util = Gauge(
            "turbo_gpu_utilization", "GPU utilization percent"
        )
        self.active_requests = Gauge(
            "turbo_active_requests", "Currently active requests"
        )
        self.safety_blocks = Counter(
            "turbo_safety_blocks_total",
            "Total safety gate blocks",
        )
