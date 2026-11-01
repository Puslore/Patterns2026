from abc import ABC, abstractmethod
from Src.Core.abstract_convertor import abstract_convertor

"""
Абстрактная фабрика для выполнения конвертации данных
"""
class abstract_convert_factory(ABC):

    """
    Подобрать и создать инстанс нужного построителя отчета
    """
    @abstractmethod
    def create(self, source:any ) -> abstract_convertor:
        pass