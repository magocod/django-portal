"""
Importador usuarios
"""

# standard library
from typing import Tuple, Dict, Any

# third-party
from rest_framework.authtoken.models import Token

# Django
from django.contrib.auth.models import User

USERS: Tuple[Dict[str, Any]] = (
    {
        'username': 'generic_admin',
        'email': 'admin@django.com',
        'password': '123',
        'first_name': 'admin',
        'last_name': 'Generic',
        'staff': True,
        'super': True,
        'token': '20fd382ed9407b31e1d5f928b5574bb4bffe6120',
    },
    {
        'username': 'generic_user',
        'email': 'user@django.com',
        'password': '123',
        'first_name': 'auser',
        'last_name': 'Generic',
        'staff': False,
        'super': False,
        'token': '20fd382ed9407b31e1d5f928b5574bb4bffe6130',
    },
)

def user_list():
    """
    migrar en db usuarios con un token
    """
    for values in USERS:
        user = User.objects.create_user(
            values['username'],
            values['email'],
            values['password']
        )
        user.first_name = values['first_name']
        user.last_name = values['last_name']
        user.is_staff = values['staff']
        user.is_superuser = values['super']
        user.save()
        Token.objects.create(key=values['token'], user_id=user.id)
    
    print('users created')
