import pytest
from db.settings import DATABASES


@pytest.fixture(scope='session')
def django_db_setup():
    """TEST시 TEST DB가 아닌 로킬 DB에 붙도록 오버라이딩"""
    DATABASES['default'] = {'ENGINE': 'django.db.backends.mysql', 'HOST': '127.0.0.1', 'NAME': 'stay', 'PORT': '3307'}


@pytest.fixture
def fixture_test():
    return 'fixture_test'
