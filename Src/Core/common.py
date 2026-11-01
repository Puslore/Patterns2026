from Src.Core.validator import argument_exception
from typing import Any, List 
from Src.Core.abstract_model import abstact_model
from Src.Dtos.entity_description_table_dto import entity_description_table_dto
from Src.Dtos.entity_description_header_dto import entity_description_header_dto


"""
Набор общих статических методо
"""
class common:

    """
    Получить полный список полей любой модели
        - is_common = True - исключить из списка словари и списки
    """
    @staticmethod
    def get_fields(source, is_common: bool = False) -> list:
        if source is None:
            return []

        items = list(filter(lambda x: not x.startswith("_") , dir(source))) 
        result = []

        for item in items:
            attribute = getattr(source.__class__, item)
            
            if isinstance(attribute, property):
                value = getattr(source, item)

                # Флаг. Только простые типы и модели включать
                if is_common == True and (isinstance(value, dict) or isinstance(value, list) ):
                    continue

                result.append(item)

        return result

    """
    Получить описание доменной сущности 
    """
    @staticmethod
    def get_entity_header(source: abstact_model) -> List[entity_description_header_dto]:
        if source is None:
            raise argument_exception("Некорректно переданы аргументы!")

        result: List[entity_description_header_dto] = []

        field_names = common.get_fields(source, is_common=True)

        for field_name in field_names:
            dto = entity_description_header_dto()
            dto.field = field_name

            try: 
                value = getattr(source, field_name) 
                value = value.unique_code if isinstance( value, abstact_model) else value
                dto.value = str(value) if value is not None else "" 
            except Exception: 
                dto.value = ""


            result.append(dto)

        return result

    from Src.Core.validator import argument_exception


    """
    Получить табличную часть для агрегата.
    Ищет первое свойство-список, берет его первый элемент (строку) 
    и формирует таблицу через get_entity_headers.
    """
    @staticmethod
    def get_entity_table(source: abstact_model) -> List[entity_description_table_dto]:
        if source is None:
            raise argument_exception("Некорректно переданы аргументы!")

        result: List[entity_description_table_dto] = []

        field_names = common.get_fields(source, is_common=False)
        list_field_name = next( (name for name in field_names if isinstance(getattr(source, name), list) and len(getattr(source, name)) > 0), None ) 
        if not list_field_name: 
            return result

        first_item = getattr(source, list_field_name)[0]
        headers = common.get_entity_header(first_item)

        table_dto = entity_description_table_dto()
        columns = [header.field for header in headers]
        table_dto.columns = columns
        values = [header.value for header in headers]
        table_dto.values = values

        result.append(table_dto)
        return result
    
