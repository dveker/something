import os
from flask import Blueprint, render_template, redirect, url_for, session, request
from seminar77.database.sql_provider import SQLProvider
from seminar77.database.select import select_dict, execute_sql
from seminar77.access import login_required

blueprint_order = Blueprint('bp_order', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_order.route('/', methods=['GET'])
@login_required
def order_index():

    sql = provider.get('product_list.sql')
    products = select_dict(sql, {})
    basket = session.get('basket', {})
    return render_template('basket_order_list.html', products=products, basket=basket)


@blueprint_order.route('/add', methods=['POST'])
@login_required
def add_to_basket():
    """Добавление товара в корзину"""
    if 'basket' not in session:
        session['basket'] = {}

    prod_id = request.form['prod_id']
    prod_name = request.form['prod_name']
    prod_price = float(request.form['prod_price'])

    if prod_id in session['basket']:
        session['basket'][prod_id]['amount'] += 1
    else:
        session['basket'][prod_id] = {
            'prod_name': prod_name,
            'prod_price': prod_price,
            'amount': 1
        }

    session.modified = True
    return redirect(url_for('bp_order.order_index'))


@blueprint_order.route('/remove/<prod_id>', methods=['POST'])
@login_required
def remove_from_basket(prod_id):
    """Удаление товара из корзины"""
    if 'basket' in session and prod_id in session['basket']:
        del session['basket'][prod_id]
        session.modified = True
    return redirect(url_for('bp_order.order_index'))


@blueprint_order.route('/clear', methods=['POST'])
@login_required
def clear_basket():
    """Очистка корзины"""
    session.pop('basket', None)
    return redirect(url_for('bp_order.order_index'))


@blueprint_order.route('/checkout', methods=['POST'])
@login_required
def checkout():

    basket = session.get('basket', {})
    user_id = session.get('user_id', 1)

    if not basket:
        return redirect(url_for('bp_order.order_index'))

    # Рассчитываем общую сумму
    total_amount = sum(item['prod_price'] * item['amount'] for item in basket.values())

    try:
        # 1. Создаем заказ
        create_order_sql = provider.get('create_order.sql')
        result = execute_sql(create_order_sql, {
            'user_id': user_id,
            'total_amount': total_amount
        })

        print(f"Create order result (affected rows): {result}")

        if result is None or result == 0:
            return render_template('order_error.html', error='Не удалось создать заказ')

        # 2. Получаем ID созданного заказа
        order_id_sql = provider.get('get_order_id.sql')
        order_id_result = select_dict(order_id_sql, {})

        print(f"Order ID result: {order_id_result}")

        if order_id_result and order_id_result[0] and order_id_result[0]['order_id']:
            order_id = order_id_result[0]['order_id']

            print(f"Created order with ID: {order_id}")

            # 3. Сохраняем товары заказа
            items_added = 0
            for prod_id, item in basket.items():
                add_item_sql = provider.get('add_order_item.sql')
                item_result = execute_sql(add_item_sql, {
                    'order_id': order_id,
                    'prod_id': int(prod_id),
                    'quantity': item['amount'],
                    'price': item['prod_price']
                })
                print(f"Add item result: {item_result}")
                if item_result is not None and item_result > 0:
                    items_added += 1

            print(f"Successfully added {items_added} items to order {order_id}")

            # 4. Очищаем корзину
            session.pop('basket', None)
            session.modified = True

            return render_template('order_success.html',
                                   order_id=order_id,
                                   total_amount=total_amount,
                                   items_count=items_added)
        else:
            return render_template('order_error.html', error='Не удалось получить ID заказа')

    except Exception as e:
        return render_template('order_error.html', error=f'Ошибка: {str(e)}')