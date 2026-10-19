from Src.Core.validator import validator

"""
Dto для описания одного элемента заголовка отчета
"""
class entity_description_header_dto:
    # Поле
    __field:str = ""

    # Значение поля
    __value:str = ""

    """
    Наименование поля
    """
    @property
    def field(self) -> str:
        return self.__field

    @field.setter
    def field(self, value: str) -> None:
        validator.validate(value, str)
        self.__field = value.strip()


    """
    Значение поля. Строковое представление.
    """
    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        self.__value = value.strip()

