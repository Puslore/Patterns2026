from Src.Core.abstract_report import abstract_report
from abc import ABC, abstractmethod
from Src.Dtos.report_type_enum import report_type_enum

"""
Абстрактная фабрика отчетов
"""
class abstract_report_factory(ABC):

    """
    Подобрать и создать инстанс нужного построителя отчета
    """
    @abstractmethod
    def create(self, report_type: report_type_enum) -> abstract_report:
        pass


    """
    Подобрать инстанс нужного построителя отчета
    """    
    @abstractmethod 
    def create_default(self) -> abstract_report:
        pass