import os
from flask import Blueprint, render_template, request
from seminar77.access import group_required
from seminar77.database.sql_provider import SQLProvider
from seminar77.database.select import select_dict
from dataclasses import dataclass


# Локальная версия model_route для query blueprint
@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str


def model_route_local(provider, user_input: dict):
    """
    Локальная версия model_route для query blueprint
    """
    err_message = ''
    print("=== DEBUG MODEL_ROUTE_LOCAL ===")
    print(f"User input: {user_input}")

    # Определяем какой SQL файл использовать
    if user_input and 'prod_category' in user_input:
        sql_file = 'product.sql'
        print("Using filtered products query (by category)")
    else:
        sql_file = 'product_all.sql'
        print("Using all products query")

    try:
        _sql = provider.get(sql_file)
        print(f"SQL query: {_sql}")
        print(f"SQL parameters: {user_input}")

        result = select_dict(_sql, user_input)
        print(f"Query result: {result}")

        if result is not None:
            if result:  # Если есть данные
                print("✓ Данные получены успешно")
                return ResultInfo(result=result, status=True, err_message=err_message)
            else:  # Если данных нет, но запрос выполнился
                err_message = 'Данные не найдены'
                print(f"⚠ {err_message}")
                return ResultInfo(result=result, status=True, err_message=err_message)
        else:  # Если произошла ошибка
            err_message = 'Ошибка выполнения запроса'
            print(f"✗ {err_message}")
            return ResultInfo(result=(), status=False, err_message=err_message)

    except Exception as e:
        err_message = f'Ошибка в model_route: {str(e)}'
        print(f"✗ {err_message}")
        import traceback
        traceback.print_exc()
        return ResultInfo(result=(), status=False, err_message=err_message)


blueprint_query = Blueprint('bp_query', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_query.route('/', methods=['GET'])
@group_required
def route_index():
    return render_template('input_category.html')


@blueprint_query.route('/', methods=['POST'])
@group_required
def route_request():
    user_input = request.form.to_dict()
    print(f"=== DEBUG QUERY ===")
    print(f"User input: {user_input}")

    # Используем локальную функцию вместо импортируемой
    result_info = model_route_local(provider, user_input)

    if result_info.status:
        products = result_info.result
        prod_title = f'Категория {user_input["prod_category"]}'
        return render_template("dynamic.html", prod_title=prod_title, products=products)
    else:
        return f'Ошибка: {result_info.err_message}'