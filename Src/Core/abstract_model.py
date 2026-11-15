from abc import ABC, abstractmethod
import uuid
from Src.Core.validator import argument_exception

"""
Абстрактный класс для наследования моделей
Содержит в себе только генерацию уникального кода
"""
class abstact_model(ABC):
    # Уникальный код
    __unique_code:str

    def __init__(self) -> None:
        super().__init__()
        self.__unique_code = uuid.uuid4().hex

    """
    Уникальный код
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code
    
    @unique_code.setter
    def unique_code(self, value: str):
        if value.strip() == "":
            raise argument_exception("value", "Некорректно передан параметр!")

        self.__unique_code = value.strip()

    """
    Перегрузка штатного варианта сравнения
    """
    def __eq__(self, value) -> bool:
        if value is  None: return False
        if not isinstance(value, abstact_model): return False

        return self.unique_code == value.unique_code

    """ Полное название класса (включая модули) """ 
    @property 
    def type(self) -> str:
         return f"{self.__class__.__module__}.{self.__class__.__qualname__}"

    @type.setter
    def type(self, value:str):
        pass

    def get_references(self) -> list:
        """Вернуть список объектов (доменных сущностей), на которые ссылается данная модель."""
        return []

    def update_from(self, source):
        """Обновить состояние модели данными из другого экземпляра того же типа."""
        if source is None or not isinstance(source, abstact_model):
            raise argument_exception("Некорректный источник для обновления модели")
        if self.unique_code != source.unique_code:
            self.unique_code = source.unique_code



