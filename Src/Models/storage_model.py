from Src.Core.entity_model import entity_model
from Src.Core.validator import validator


"""
Модель склада
"""
class storage_model(entity_model):
    """Склад с наименованием и адресом."""

    __address:str = ""

    def __init__(self):
        super().__init__()
        
    """
    Адрес
    """
    @property
    def address(self) -> str:
        return self.__address.strip()
    
    @address.setter
    def address(self, value:str):
        validator.validate(value, str)
        self.__address = value.strip()

    def update_from(self, source):
        """Обновить состояние склада из валидированного объекта."""
        super().update_from(source)
        self.address = source.address

    @staticmethod
    def create_main():
        """Создать основной склад приложения."""
        result = storage_model()
        result.name = "Основной склад"
        result.address = "Иркутск, ул. Высокого Полета, д.100"
        return result

    