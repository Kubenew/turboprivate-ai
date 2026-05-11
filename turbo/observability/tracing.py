from opentelemetry import trace


class Tracer:
    def __init__(self, service_name: str = "turboprivate"):
        self.service_name = service_name
        self.tracer = trace.get_tracer(service_name)

    async def instrument_fastapi(self, app):
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app, tracer_provider=self.tracer)
