import os
from flask import Blueprint, render_template, request, session, flash
from seminar77.access import group_required, login_required
from seminar77.database.sql_provider import SQLProvider
from seminar77.database.select import execute_sql, select_dict


blueprint_report = Blueprint('bp_report', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))





@blueprint_report.route('/', methods=['GET'])
@login_required
@group_required
def report_index():
    user_group = session.get('user_group')
    permissions = get_report_permissions(user_group)
    return render_template('report_menu.html',
                           user_group=user_group,
                           permissions=permissions)


@blueprint_report.route('/create', methods=['GET'])
@login_required
@group_required
def create_report():
    user_group = session.get('user_group')
    permissions = get_report_permissions(user_group)

    if not permissions['can_create']:
        flash('Нет прав для создания отчетов', 'error')
        return render_template('report_menu.html',
                               user_group=user_group,
                               permissions=permissions)

    return render_template('create_report.html')


@blueprint_report.route('/create', methods=['POST'])
@login_required
@group_required
def create_report_process():
    user_group = session.get('user_group')
    permissions = get_report_permissions(user_group)

    if not permissions['can_create']:
        flash('Нет прав для создания отчетов', 'error')
        return render_template('report_menu.html',
                               user_group=user_group,
                               permissions=permissions)

    user_input = request.form.to_dict()

    # Валидация ввода - проверяем все 4 поля
    required_fields = ['month', 'year', 'amount', 'value']
    for field in required_fields:
        if not user_input.get(field):
            flash('Заполните все поля', 'error')
            return render_template('create_report.html')

    try:
        month = int(user_input['month'])
        year = int(user_input['year'])
        amount = int(user_input['amount'])
        value = float(user_input['value'])

        if month not in range(1, 13):
            flash('Месяц должен быть от 1 до 12', 'error')
            return render_template('create_report.html')

        if amount < 0:
            flash('Количество товаров не может быть отрицательным', 'error')
            return render_template('create_report.html')

        if value < 0:
            flash('Стоимость не может быть отрицательной', 'error')
            return render_template('create_report.html')

    except ValueError:
        flash('Проверьте правильность введенных данных', 'error')
        return render_template('create_report.html')

    # Все 4 параметра от пользователя
    sql_params = {
        'month': month,
        'year': year,
        'amount': amount,
        'value': value
    }

    # Выполняем запрос
    sql = provider.get('create_report.sql')
    print(f"=== CREATE REPORT SQL ===")
    print(f"SQL: {sql}")
    print(f"Params: {sql_params}")

    result = execute_sql(sql, sql_params)
    print(f"Result: {result}")

    if result is not None and result > 0:
        flash('Отчёт успешно создан', 'success')
    elif result == 0:
        flash('Отчёт не был создан', 'warning')
    else:
        flash('Ошибка при создании отчёта', 'error')

    return render_template('create_report.html')


def get_report_permissions(user_group):
    """Возвращает доступные действия для пользователя"""
    permissions = {
        'can_create': user_group in ['manager', 'admin'],
        'can_view': user_group == 'admin'
    }
    return permissions

@blueprint_report.route('/view', methods=['GET'])
@login_required
@group_required
def view_report():
    user_group = session.get('user_group')
    permissions = get_report_permissions(user_group)

    if not permissions['can_view']:
        flash('Нет прав для просмотра отчетов', 'error')
        return render_template('report_menu.html',
                               user_group=user_group,
                               permissions=permissions)

    return render_template('view_report.html')


@blueprint_report.route('/view', methods=['POST'])
@login_required
@group_required
def view_report_process():
    user_group = session.get('user_group')
    permissions = get_report_permissions(user_group)

    if not permissions['can_view']:
        flash('Нет прав для просмотра отчетов', 'error')
        return render_template('report_menu.html',
                               user_group=user_group,
                               permissions=permissions)

    user_input = request.form.to_dict()

    # Валидация ввода
    if not user_input.get('month') or not user_input.get('year'):
        flash('Заполните все поля', 'error')
        return render_template('view_report.html')

    try:
        month = int(user_input['month'])
        year = int(user_input['year'])
        if month not in range(1, 13):
            flash('Месяц должен быть от 1 до 12', 'error')
            return render_template('view_report.html')
    except ValueError:
        flash('Месяц и год должны быть числами', 'error')
        return render_template('view_report.html')

    # Выполняем запрос
    sql = provider.get('get_report.sql')
    print(f"=== VIEW REPORT SQL ===")
    print(f"SQL: {sql}")
    print(f"Params: {user_input}")

    reports = select_dict(sql, user_input)
    print(f"Reports: {reports}")

    if reports is not None:
        if reports:
            prod_title = f'Отчёт за {month:02d}.{year}'
            return render_template('report_results.html', prod_title=prod_title, products=reports)
        else:
            flash('Отчёт не найден', 'warning')
    else:
        flash('Ошибка при получении отчёта', 'error')

    return render_template('view_report.html')