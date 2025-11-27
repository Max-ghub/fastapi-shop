from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app: FastAPI) -> None:
    (
        Instrumentator(excluded_handlers=["/metrics"])
        .instrument(app)
        .expose(
            app,
            endpoint="/metrics",
            include_in_schema=False,
        )
    )
