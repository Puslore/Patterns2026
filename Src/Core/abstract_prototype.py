from abc import ABC, abstractmethod
from Src.Dtos.filter_dto import filter_dto


class abstract_prototype(ABC):
    """
    Абстрактный класс шаблона Прототип для фильтрации и клонирования данных
    """

    @abstractmethod
    def clone(self, filter: filter_dto) -> "abstract_prototype":
        """
        Склонировать прототип с фильтрацией данных по DTO модели
        """
        pass
