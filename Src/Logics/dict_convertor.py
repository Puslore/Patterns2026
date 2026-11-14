from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.validator import validator, operation_exception
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
import importlib

"""
Конвертация словаря
"""
class dict_convertor(abstract_convertor):
    # Фабрика для подбора конвертора
    __convert_factory:abstract_convert_factory = None
    # Маппинг
    __mapping_factory:abstract_mapping_factory = None

    def __init__(self, convert_factory: abstract_convert_factory, mapping_factory: abstract_mapping_factory):
        super().__init__()
        validator.validate(convert_factory, abstract_convert_factory)
        self.__convert_factory = convert_factory
        validator.validate(mapping_factory, abstract_mapping_factory )
        self.__mapping_factory = mapping_factory

    """
    Выполнить сериализацию
    """ 
    def serialize(self, field: str, items:any) -> dict:
        validator.validate(items, dict)

        result =  {}
        for key in items.keys():
            value = items [ key ]
            convertor = self.__convert_factory.create( value )
            result_convert = convertor.serialize( field, value )
            result[ key ] = result_convert[ field ]

        return result
           

    """
    Выполнить десериализацию
    """
    def deserialize(self, source: dict ) -> object:
        validator.validate( source, dict)
        if len(source.keys()) == 0:
              raise operation_exception("Для десериализации требуется заполненный словарь!")  

        # Указан четко тип
        if "type" in source.keys():
            try:
                # Создаем Dto
                module_path, class_name = source["type"].rsplit('.', 1) 
                module = importlib.import_module(module_path)
                dto_type = getattr(module, class_name)
                dto = dto_type().from_dict( source )

                # Получаем Domain
                domain = self.__mapping_factory.to_model( dto )
                return domain
            except Exception as ex:
                self.set_exception(ex)
            
        # Обычный словарь
        result = {}
        # Обеспечиваем порядок десериализации с учетом зависимостей доменных моделей
        priority_order = ["range_model", "group_model", "storage_model", "nomenclature_model", "ingredient_model", "receipt_model"]
        def sort_key(k):
            return priority_order.index(k) if k in priority_order else len(priority_order)

        for key in sorted(source.keys(), key=sort_key):
            value = source[ key ]
            convertor = self.__convert_factory.create( value )
            result_convert = convertor.deserialize( value )
            result[ key ] = result_convert

        return result    
