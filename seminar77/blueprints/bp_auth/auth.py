import os
from flask import Blueprint, render_template, session, request, redirect, url_for, current_app
from seminar77.database.sql_provider import SQLProvider  # УБРАТЬ seminar55.
from seminar77.database.DBcm import DBContextManager  # УБРАТЬ seminar55.

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

@auth_bp.route('/', methods=['GET', 'POST'])
def auth_index():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"=== DEBUG AUTH ===")
        print(f"Login attempt: {username}")

        try:
            sql_query = provider.get('user.sql')
            print(f"SQL query: {sql_query}")

            with DBContextManager(current_app.config['db_config']) as cursor:
                if cursor is None:
                    print("Cursor is None - connection failed")
                    return render_template('login.html', error='Ошибка подключения к БД')

                print("Database connection successful")
                cursor.execute(sql_query, (username, password))
                user_data = cursor.fetchone()

                print(f"Database result: {user_data}")

                if user_data:
                    session['user_id'] = user_data[0]
                    session['user_group'] = user_data[1]
                    session['logged_in'] = True

                    print(f"Session SET: user_id='{user_data[0]}', user_group='{user_data[1]}'")
                    return redirect(url_for('main_menu'))
                else:
                    print("No user found or wrong password")
                    return render_template('login.html', error='Неверное имя пользователя или пароль')

        except Exception as e:
            print(f"Database error: {str(e)}")
            import traceback
            traceback.print_exc()
            return render_template('login.html', error=f'Ошибка базы данных: {str(e)}')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.auth_index'))