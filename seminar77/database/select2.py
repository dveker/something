from flask import current_app

from seminar55.database.DBcm import DBContextManager


def select_list(_sql: str, param_list: list) -> tuple:
    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:  # Удалось ли подключиться?
            raise ValueError('Не удалось подключиться')  # Генерирует фиктивную ошибку
        else:
            cursor.execute(_sql, param_list)
            result = cursor.fetchall()
            schema = []
            for item in cursor.description:
                schema.append(item[0])
            print(schema)
        return result, schema


def select_dict(_sql, user_dict: dict):
    user_list = []
    for key in user_dict:
        user_list.append(user_dict[key])
    print('user_list in select_dict', user_list)
    result, schema = select_list(_sql, user_list)
    result_dict = []
    for item in result:
        result_dict.append(dict(zip(schema, item)))
    print(result_dict)
    return result_dict
