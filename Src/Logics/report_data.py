from decimal import Decimal
from enum import Enum

from Src.Core.abstract_model import abstact_model
from Src.Core.common import common


def to_report_data(value, ancestors=None):
    """Преобразовать модель и ее связанные данные в сериализуемые значения."""
    ancestors = ancestors or frozenset()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (list, tuple)):
        return [to_report_data(item, ancestors) for item in value]
    if isinstance(value, dict):
        return {str(key): to_report_data(item, ancestors)
                for key, item in value.items()}
    if isinstance(value, abstact_model):
        if id(value) in ancestors:
            return {"unique_code": value.unique_code, "name": value.name}
        nested_ancestors = ancestors | {id(value)}
        return {
            field: to_report_data(getattr(value, field), nested_ancestors)
            for field in sorted(common.get_fields(value))
        }
    raise TypeError(f"Неподдерживаемый тип данных отчета: {type(value).__name__}")


def flatten_report_data(data, prefix=""):
    """Развернуть вложенные значения в пары путь-значение для табличных форматов."""
    rows = []
    if isinstance(data, dict):
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else key
            rows.extend(flatten_report_data(value, path))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            rows.extend(flatten_report_data(value, f"{prefix}[{index}]"))
        if not data:
            rows.append((prefix, "[]"))
    else:
        rows.append((prefix, "" if data is None else str(data)))
    return rows
