from Src.Models.receipt_model import receipt_model
from Src.Dtos.ingredient_dto import ingredient_dto
from Src.Core.validator import validator, operation_exception
from Src.Core.abstract_dto import abstract_dto
from Src.Models.ingredient_model import ingredient_model

"""
Dto для описания рецепта (агрегат)
"""
class receipt_dto (abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование
    __name: str = ""

    # Список ингредиентов
    __items: list[str] = None

    # Вес брутто
    __brutto: int = 0

    # Вес нетто
    __netto: int = 0

    # Описание процесса
    __comments: str = ""

    def __init__(self) -> None:
        # Инициализация пустого списка, чтобы избежать мутации класса
        if self.__items is None:
            self.__items = []

    """
    Код
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        self.__unique_code = value.strip()

    """
    Наименование
    """
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value.strip()

    """
    Состав рецепта
    """
    @property
    def items(self) -> list:
        return self.__items

    @items.setter
    def items(self, value: list) -> None:
        self.__items = value

    """
    Вес брутто
    """
    @property
    def brutto(self) -> int:
        return self.__brutto

    @brutto.setter
    def brutto(self, value: int) -> None:
        self.__brutto = value

    """
    Вес нетто
    """
    @property
    def netto(self) -> int:
        return self.__netto

    @netto.setter
    def netto(self, value: int) -> None:
        self.__netto = value

    """
    Описание процесса
    """
    @property
    def comments(self) -> str:
        return self.__comments

    @comments.setter
    def comments(self, value: str) -> None:
        self.__comments = value.strip()

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: receipt_model) -> "receipt_dto":
        validator.validate(source, receipt_model)
        
        dto = receipt_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.brutto = source.brutto
        dto.netto = source.netto
        dto.comments = source.comments

        # Преобразуем список доменных моделей ингредиентов в список DTO
        dto.items = []
        for item in source.items:
            dto.items.append( item.unique_code )
            
        return dto

    """
    Выполнить маппинг в доменную модель
    """
    def mapping(self, cache: dict) -> receipt_model:
        super().mapping(cache)

        domain = receipt_model()
        domain.unique_code = self.unique_code
        domain.name = self.name
        if self.comments and self.comments.strip() != "":
            domain.comments = self.comments

        for item in self.items:
            if item in cache.keys():
                ingredient = cache[ item ]
                domain.add( ingredient )

        cache[ domain.unique_code ] = domain
        return domain    

    """
    Фабричный метод для создания DTO из словаря
    """
    def from_dict(self, source:dict) -> "receipt_dto":
        validator.validate(source, dict)

        dto = receipt_dto()
        dto.unique_code = self.try_get_value("unique_code", source)
        dto.name = self.try_get_value("name", source)
        dto.comments = self.try_get_value("comments", source)
        dto.brutto = self.try_get_value("brutto", source)
        dto.netto = self.try_get_value("netto", source)
        dto.items = self.try_get_value("items", source)

        return dto

