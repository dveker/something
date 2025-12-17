from dataclasses import dataclass
from seminar77.database.select import select_dict

@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str


def model_route(provider, sql_file_name, user_input: dict):
    err_message = ''
    _sql = provider.get(sql_file_name)
    print(f"=== MODEL ROUTE: SQL={_sql} ===")
    print(f"=== MODEL ROUTE: user_input={user_input} ===")

    result = select_dict(_sql, user_input)
    print('result from select_dict=', result)

    if result is not None:
        if result:
            return ResultInfo(result=result, status=True, err_message=err_message)
        return ResultInfo(result=result, status=True, err_message='Данные не получены')
    else:
        return ResultInfo(result=(), status=False, err_message='Не удалось подключиться к БД')