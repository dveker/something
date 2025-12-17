import os
from flask import Blueprint, render_template, request
from seminar77.access import group_required
from seminar77.database.sql_provider import SQLProvider
from seminar77.database.select import select_dict
from dataclasses import dataclass


# Локальная версия для query
@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str


def model_route_query(provider, user_input: dict):
    err_message = ''
    print("=== DEBUG MODEL_ROUTE_QUERY ===")

    if user_input and 'prod_category' in user_input:
        sql_file = 'product.sql'
    else:
        sql_file = 'product_all.sql'

    try:
        _sql = provider.get(sql_file)
        result = select_dict(_sql, user_input)

        if result is not None:
            if result:
                return ResultInfo(result=result, status=True, err_message=err_message)
            else:
                return ResultInfo(result=result, status=True, err_message='Данные не найдены')
        else:
            return ResultInfo(result=(), status=False, err_message='Ошибка выполнения запроса')
    except Exception as e:
        return ResultInfo(result=(), status=False, err_message=f'Ошибка: {str(e)}')


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
    result_info = model_route_query(provider, user_input)

    if result_info.status:
        products = result_info.result
        prod_title = f'Категория {user_input["prod_category"]}'
        return render_template("dynamic.html", prod_title=prod_title, products=products)
    else:
        return f'Ошибка: {result_info.err_message}'