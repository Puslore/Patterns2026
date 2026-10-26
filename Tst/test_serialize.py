from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Dtos.group_dto import group_dto
from Src.Logics.basic_convertor import basic_convertor
from Src.Core.common import common
import pytest

"""
Проверить сериализацию полей group_dto через basic_convertor с использованием common.get_fields.
"""
def test_group_dto_fields_serialization():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    domain = manager.data[storage_manager.group_key()][0]
    dto = group_dto.from_domain_model(domain)
    convertor = basic_convertor()
    fields = common.get_fields(dto, is_common=True)
    result = {}

    # Действие
    for field in fields:
        value = getattr(dto, field)
        result.update ( convertor.serialize(field, value))

    # Проверки
    assert convertor.error_text == ""
    assert result["unique_code"] == domain.unique_code
    assert result["name"] ==  domain.name