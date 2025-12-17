from seminar77.database.DBcm import DBContextManager
from flask import current_app


def select_dict(_sql, user_input: dict):
    print(f"=== DEBUG SELECT_DICT ===")
    print(f"SQL: {_sql}")
    print(f"Input: {user_input}")

    try:
        with DBContextManager(current_app.config['db_config']) as cursor:
            if cursor is None:
                print("Cursor is None")
                return None

            # Преобразуем словарь в список параметров
            params = list(user_input.values()) if user_input else []
            print(f"Params: {params}")

            if params:
                cursor.execute(_sql, params)
            else:
                cursor.execute(_sql)

            result = cursor.fetchall()
            print(f"Raw result from DB: {result}")

            # Преобразуем в список словарей
            if result:
                columns = [col[0] for col in cursor.description]
                print(f"Columns: {columns}")

                result_dict = []
                for row in result:
                    row_dict = dict(zip(columns, row))
                    result_dict.append(row_dict)
                    print(f"Row: {row_dict}")

                print(f"Final dict result: {result_dict}")
                return result_dict
            else:
                print("No results from DB")
                return []

    except Exception as e:
        print(f"Error in select_dict: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def execute_sql(_sql, user_input: dict):
    """Выполняет INSERT, UPDATE, DELETE запросы"""
    print(f"=== DEBUG EXECUTE_SQL ===")
    print(f"SQL: {_sql}")
    print(f"Input: {user_input}")

    try:
        with DBContextManager(current_app.config['db_config']) as cursor:
            if cursor is None:
                print("Cursor is None")
                return None

            # Преобразуем словарь в список параметров
            params = list(user_input.values()) if user_input else []
            print(f"Params: {params}")

            if params:
                cursor.execute(_sql, params)
            else:
                cursor.execute(_sql)

            # Для INSERT возвращаем количество затронутых строк
            affected_rows = cursor.rowcount
            print(f"Affected rows: {affected_rows}")
            return affected_rows

    except Exception as e:
        print(f"Error in execute_sql: {str(e)}")
        import traceback
        traceback.print_exc()
        return None