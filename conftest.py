"""
Ajustes pruebas
"""

# third-party
import pytest

from rest_framework.test import APIClient

# Django
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Cargar bd de prueba
    """
    with django_db_blocker.unblock():
        call_command('default_db')


@pytest.fixture
def admin_client():
    """
    Iniciar cliente pruebas (superusuario)
    """
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + '20fd382ed9407b31e1d5f928b5574bb4bffe6d30')
    return client

@pytest.fixture
def user_client():
    """
    Iniciar cliente pruebas (vendedor)
    """
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + '20fd382ed9407b31e1d5f928b5574bb4bffe6130')
    return client

@pytest.fixture
def public_client():
    """
    Iniciar cliente pruebas (no autenticado)
    """
    client = APIClient()
    return client
