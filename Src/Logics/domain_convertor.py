from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.validator import validator
from Src.Core.abstract_model import abstact_model
from Src.Core.entity_model import entity_model
from Src.Core.common import common
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.validator import operation_exception


"""
Конвертор доменных сущностей
"""
class domain_convertor(abstract_convertor):
    # Фабрика для подбора конвертора
    __convert_factory:abstract_convert_factory = None
    # Фабрика для маппинга 
    __mapping_factory:abstract_mapping_factory = None

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
        result = {}

        dto = self.__mapping_factory.to_dto( object )
        fields = common.get_fields( dto )

        for item in fields:
            value = getattr( dto, item )    
            convertor = self.__convert_factory.create( value )
            value_dto = self.__mapping_factory.to_dto( value )
            if value_dto is None:
                 raise operation_exception(f"Невозможно сопоставить тип {type(value).__name__}!")

            inner_result = convertor.serialize( item, value_dto )
            result[ item ] = inner_result [ item ]
 
        return { field: result }    


    """
    Переопределенный метод для десериализации
    """    
    def deserialize(self, source) -> object:
        super().deserialize(source) 
        pass