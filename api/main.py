import json
import logging
import os
import base64
import django
from django.conf import settings
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from common.exceptions import ApplicationError
from api.api_comment import DESCRIPTION
from fastapi.middleware.cors import CORSMiddleware


ENV = os.getenv('ENV', 'local')
FIREBASE_CREDENTIAL = os.getenv('FIREBASE_CREDENTIAL')
SENTRY_DSN = 'https://694f3e392bd74d179a9f5a36d42c2f60@o348151.ingest.sentry.io/4504654721581056'
THREADS_LIMIT = 5

logger = logging.getLogger(__name__)
origins = [
    "http://localhost:3000",
    "https://www.goldhand.app",
    "https://admin.goldhand.app",
    "https://goldhand.app",
]


def configure_sentry(sentry_dsn: str):
    return


def configure_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db.settings')
    from django.conf import settings

    try:
        settings.INSTALLED_APPS
    except Exception as exc:
        raise exc

    if settings.configured:
        django.setup()


def configure_app() -> FastAPI:

    app = FastAPI(title='GENE API', version='0.1.0', description=DESCRIPTION)

    _patch_django_connection(app)
    _add_routers(app)
    _add_exception_handlers(app)

    handlers_to_apply = {}
    for ex, func in app.exception_handlers.items():
        handlers_to_apply[ex] = func

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


def configure_firebase():
    return


def _patch_django_connection(app):
    '''Add some signal handlers from django requests'''

    @app.middleware('http')
    async def add_process_time_header(request: Request, call_next):
        response = await call_next(request)
        django.core.signals.request_finished.send(sender=app.__class__)
        return response


def _add_exception_handlers(app):
    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError):
        logger.error('application error', exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={'error': exc.to_dict()},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={'error': {'code': exc.status_code, 'message': exc.detail}},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        errors = []
        for err in exc.errors():
            error = {
                'code': 422,
                'message': err['msg'],
            }
            if err['type'] == 'value_error.missing':
                error['field'] = err['loc'][-1]
                error['description'] = f'field \'{error["field"]}\' is required.'
            errors.append(error)

        return JSONResponse(
            status_code=400,
            content={
                'error': {
                    'code': 422,
                    'message': errors[0]['message'],
                    'errors': errors,
                },
            },
        )

    debug = os.getenv('DEBUG', False)
    if debug:

        @app.exception_handler(Exception)
        def unknown_exception_handler(request: Request, exc: Exception):
            return JSONResponse(
                status_code=500,
                content={
                    'error': {
                        'code': 500,
                        'message': f'{exc.__class__.__name__}: {str(exc)}',
                    }
                },
            )

    return app


def _add_routers(app):
    from api.routers import health, file

    router = app

    router.include_router(file.router, tags=['File'])


configure_django()
configure_sentry(SENTRY_DSN)
configure_firebase()
app = configure_app()


@app.on_event('startup')
async def app_startup():
    print('app startup ok. ENV =', ENV)
    pass


@app.on_event("shutdown")
def shutdown_event():
    pass
