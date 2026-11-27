from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.validator import validator
from Src.Core.common import common
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.validator import operation_exception
import importlib


"""
Конвертор доменных сущностей
"""
class domain_convertor(abstract_convertor):
    # Фабрика для подбора конвертора
    __convert_factory:abstract_convert_factory = None
    # Фабрика для маппинга 
    __mapping_factory:abstract_mapping_factory = None

    # Singletone
    def __new__(cls, convert_factory: abstract_convert_factory, mapping_factory: abstract_mapping_factory):
        if not hasattr(cls, '_instance'):
            cls._instance = super(domain_convertor, cls).__new__(cls)
        return cls._instance

    def __init__(self, convert_factory: abstract_convert_factory, mapping_factory: abstract_mapping_factory ):
        super().__init__()
        validator.validate(convert_factory, abstract_convert_factory)
        self.__convert_factory = convert_factory
        validator.validate(mapping_factory, abstract_mapping_factory)
        self.__mapping_factory = mapping_factory


    """
    Абстрактная фабрика для конвертации данных
    """
    @property
    def factory(self) ->   abstract_convert_factory:
        return self.__convert_factory  

    
    """
    Переопределенный метод для сериализации
    """
    def serialize(self, field: str, object: any) -> dict:
        super().serialize(field, object)

        dto = self.__mapping_factory.to_dto( object )
        target = dto if dto is not None else object
        result = {}
        fields = common.get_fields( target )

        for item in fields:
            value = getattr( target, item )
            if value is None:
                result[ item ] = None
                continue

            convertor = self.__convert_factory.create( value )
            inner_result = convertor.serialize( item, value )
            result[ item ] = inner_result [ item ]

        return { field: result }


    """
    Переопределенный метод для десериализации
    """    
    def deserialize(self, source: dict) -> object:
        pass
        