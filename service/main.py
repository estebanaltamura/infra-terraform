from fastapi import FastAPI
from service.api import branches, available_stable_environments, services, create_ephemeral_backend, create_no_ephemeral_backend

app = FastAPI()

# Incluyendo endpoints
app.include_router(branches.router, prefix="/repos", tags=["branches"])
app.include_router(available_stable_environments.router, prefix="/available-stable-environments", tags=["available-stable-environments"])
app.include_router(services.router, prefix="/services", tags=["services"])
app.include_router(create_ephemeral_backend.router, prefix="/create-ephemeral-backend", tags=["create-ephemeral-backend"])
app.include_router(create_no_ephemeral_backend.router, prefix="/create-no-ephemeral-backend", tags=["create-no-ephemeral-backend"])



