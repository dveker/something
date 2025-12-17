from functools import wraps
from flask import session, redirect, url_for, flash
import json
import os


def load_access_config():
    """Загружает конфигурацию прав доступа"""
    config_path = os.path.join(os.path.dirname(__file__), 'data', 'db_access.json')
    with open(config_path) as f:
        return json.load(f)


def group_required(f):
    """Декоратор для проверки прав доступа"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth_bp.auth_index'))

        user_group = session.get('user_group')
        access_config = load_access_config()

        # Получаем имя blueprint из имени функции
        blueprint_name = f.__module__.split('.')[-2] if '.' in f.__module__ else f.__module__
        print(f"=== DEBUG ACCESS ===")
        print(f"User group: {user_group}")
        print(f"Blueprint name: {blueprint_name}")
        print(f"Access config: {access_config}")

        if user_group in access_config:
            allowed_blueprints = access_config[user_group]
            if blueprint_name in allowed_blueprints:
                return f(*args, **kwargs)

        flash('У вас нет прав для доступа к этой странице', 'error')
        return redirect(url_for('main_menu'))

    return decorated_function


def login_required(f):
    """Декоратор для проверки авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth_bp.auth_index'))
        return f(*args, **kwargs)
    return decorated_function