from abc import ABC

"""
Абстрактный класс для реализации загрузки и обработки данных
"""
class abstract_manager(ABC):
# Флаг. Загрузка и обработка завершена успешно
    __is_loaded:bool = False
   
    """
    Загрузить данные
    """
    def load(self, file_name:str = "") -> None:
        pass

    """
    Обработать загруженные данные
    """    
    def build(self) -> bool:
        return False

    """
    Флаг. Данные подготовлены
    """
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded    

