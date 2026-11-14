from abc import ABC, abstractmethod

"""
Абстрактная фабрика для конвертации сущностей Dto vs Domain
"""
class abstract_mapping_factory(ABC):

    """
    Сконвертировать доменную модель в Dto
    """
    @abstractmethod   
    def to_dto(self, source: object) -> object:
        pass

    """
    Сконвертировать Dto в доменную модель
    """
    @abstractmethod       
    def to_model(self, source: object) -> object:
        pass