from abc import ABC, abstractmethod

"""
Элемент наблюдения
"""
class abstract_observabile(ABC):

    """
    Выполнить обработку события
    """
    @abstractmethod
    def handler( self, event_types :str, params: object = None) -> None:
        pass