from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
import logging.config
from starlette.middleware.base import BaseHTTPMiddleware
import json
from contextvars import ContextVar
from uuid import uuid4

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.events import startup_event_handler, shutdown_event_handler

# Preferred method: Load logging configuration from JSON using dictConfig.
with open("logging_config.json", "r") as f:
    config_dict = json.load(f)
logging.config.dictConfig(config_dict)
logger = logging.getLogger(__name__)

# Legacy method (commented out):
# Loads configuration via fileConfig.
# Not ideal for JSON configurations.
# logging.config.fileConfig('logging_config.json', disable_existing_loggers=False)
# logger = logging.getLogger(__name__)

# Create request ID context
request_id_contextvar = ContextVar("request_id", default=None)

# Define middleware for tracking request duration
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid4())
        request_id_contextvar.set(request_id)
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Get start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add timing headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        # Log request
        logger.info(
            "Request processed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "processing_time": process_time,
                "status_code": response.status_code
            }
        )
        
        return response


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="Enterprise-level FastAPI application",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Set CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add timing middleware
    application.add_middleware(TimingMiddleware)

    # Add event handlers
    application.add_event_handler("startup", startup_event_handler(application))
    application.add_event_handler("shutdown", shutdown_event_handler(application))

    # Add routers
    application.include_router(api_router, prefix=settings.API_V1_STR)

    @application.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, exc):
        logger.error(
            f"HTTP error occurred: {exc.detail}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "status_code": exc.status_code,
                "method": request.method,
                "path": request.url.path
            }
        )
        return await http_exception_handler(request, exc)

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        errors = []
        for error in exc.errors():
            error_detail = {
                "location": error["loc"],
                "message": error["msg"],
                "type": error["type"]
            }
            errors.append(error_detail)
        
        logger.warning(
            "Validation error",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "method": request.method,
                "path": request.url.path,
                "errors": errors
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": errors}
        )

    @application.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return application


app = create_application()