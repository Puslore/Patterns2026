from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.validator import validator
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.validator import operation_exception

"""
Конвертация списка
"""
class list_convertor(abstract_convertor):
     # Фабрика для подбора конвертора
    __convert_factory:abstract_convert_factory = None
     # Фабрика для маппинга 
    __mapping_factory:abstract_mapping_factory = None

    def __init__(self, convert_factory: abstract_convert_factory, mapping_factory: abstract_mapping_factory):
        super().__init__()
        validator.validate(convert_factory, abstract_convert_factory)
        self.__convert_factory = convert_factory
        validator.validate(mapping_factory, abstract_mapping_factory)
        self.__mapping_factory = mapping_factory

    
    """
    Выполнить сериализацию
    """ 
    def serialize(self, field: str, items:any) -> dict:
        validator.validate(items, list)

        result = []
        for item in items:
            convertor = self.__convert_factory.create( item )
            dto = self.__mapping_factory.to_dto( item )
            
            if dto is None:
                raise operation_exception(f"Невозможно подобрать Dto объект для {type(item)}!")
            
            convert_result = convertor.serialize( field, dto )
            result.append( convert_result[ field ] )

        return { field: result }  
            

    """
    Выполнить десериализацию
    """
    def deserialize(self, source: any ) -> object:
        validator.validate( source, list)
        if len(source) == 0:
            return []

        result = []
        for item in source:
            convertor = self.__convert_factory.create( item )
            domain = convertor.deserialize( item )
            if domain is None:
                raise operation_exception(f"Невозможно подобрать Domain объект для {type(item)}!")

            result.append( domain )

        return result    
            