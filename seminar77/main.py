import json
import os

from flask import Flask, render_template, session, redirect, url_for
from blueprints.bp_report.report import blueprint_report
from blueprints.order.order_route import blueprint_order
from blueprints.bp_auth.auth import auth_bp
from blueprints.bp_query.query import blueprint_query

app = Flask(__name__)
with open('./data/db_config.json') as f:
    app.config['db_config'] = json.load(f)

# Секретный ключ для сессий
app.secret_key = 'your-secret-key-here'

# Регистрация blueprint'ов
app.register_blueprint(blueprint_order, url_prefix='/order')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(blueprint_query, url_prefix='/query')
app.register_blueprint(blueprint_report, url_prefix='/report')


def get_main_menu_permissions(user_group):
    """Возвращает доступные действия для главного меню"""
    return {
        'can_query': user_group == 'admin'
    }


@app.route('/', methods=['GET'])
def main_menu():
    # Проверяем авторизацию
    if not session.get('logged_in'):
        return redirect(url_for('auth_bp.auth_index'))

    user_group = session.get('user_group')
    permissions = get_main_menu_permissions(user_group)

    return render_template('main.html',
                           user_group=user_group,
                           permissions=permissions)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.auth_index'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)