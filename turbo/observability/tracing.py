from opentelemetry.sdk.trace import TracerProvider


class Tracer:
    def __init__(self, service_name: str = "turboprivate"):
        self.service_name = service_name
        self.tracer_provider = TracerProvider()
        self.tracer = self.tracer_provider.get_tracer(service_name)

    async def instrument_fastapi(self, app):
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app, tracer_provider=self.tracer_provider)
