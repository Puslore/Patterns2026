"""
Dto для описание одной строки табличной части
"""
class entity_description_table_dto:
    # Список колонок
    __columns:list[str]

    # Список значений
    __values:list[str]

    def __init__(self):
        self.__columns = []
        self.__values = []


    """
    Список колонок
    """
    @property
    def columns(self) -> list[str]:
        return self.__columns

    @columns.setter
    def columns(self, value:list[str]) -> None:
        self.__columns = value

    """
    Список значений
    """
    @property
    def values(self) -> list[str]:
        return self.__values

    @values.setter
    def values(self, value:list[str]) -> None:
        self.__values = value

