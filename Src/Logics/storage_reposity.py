from Src.Core.abstract_model import abstact_model
from Src.Core.entity_model import entity_model
from Src.Core.validator import validator, operation_exception
from Src.Core.common import common

"""
Репозиторий для хранения списка объектов и счетчика связей
"""
class storage_repository:
    # Исходный набор данных. Ключ - GUID, значение- abstract_model
    __data:dict = {}
    # Счетчик ссылков. Ключ - GUID, значение - число ссылок
    __counts:dict = {}

    """
    Зарегистрировать доменный объект
    """
    def registry(self, source: abstact_model):
        validator.validate( source, abstact_model)

        # Регистрируем основной объект
        self.__data [ source.unique_code ] = source
        if source.unique_code in self.__counts.keys():
            self.__counts[ source.unique_code ] += 1
        else:
            self.__counts[ source.unique_code ] = 0    

        # Регистрируем вложения
        fields = common.get_fields( source, False )
        for field in fields:
            value = getattr( source, field )
            if isinstance( value, (abstact_model, entity_model) ):
                self.registry( value )

    """
    Зарегистрировать сразу же несколько объектов
    """
    def registry_range(self, items:list ):
        validator.validate( items, list )
        for item in items:
            self.registry( item )

    """
    Получить объект по уникальному коду
    """
    def get(self, source: str):
        validator.validate( source, str)

        if source in self.__data.keys():
            return self.__data.get( source )   
        else:
            raise operation_exception(f"Не найдена доменная сущность по коду : {source}!")

    """
    Проверить возможность удаления
    """
    def can_delete(self, source: abstact_model) -> bool:
        validator.validate( source, abstact_model) 

        try:
            self.get( source.unique_code )

            if self.__counts[ source.unique_code ] > 0:
                # Есть связи
                return False
            else:
                return True
        except:
            # Не найдено
            return False  

    """
    Удалить сущность из счетчиков
    """
    def delete(self, source: abstact_model):
        validator.validate(source, abstact_model)
        if not self.can_delete( source ):
            raise operation_exception(f"Невозможно удалить запись {source.unique_code}!")

        self.__data.pop ( source.unique_code, None )
        self.__counts.pop ( source.unique_code, None )

    """
    Исходный набор данных
    """
    @property
    def data(self) -> dict:    
        return self.__data

    """
    Исходный набор счетчиков
    """
    @property
    def counts(self) -> dict:
        return self.__counts

          

