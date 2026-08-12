"""
FastAPI application factory for Confidential Computing Control Plane.
"""

from fastapi import FastAPI

from cc_framework.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Confidential Computing Research Framework API",
        description="Remote Attestation Authority & Policy Verification Service",
        version="1.0.0",
    )
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
