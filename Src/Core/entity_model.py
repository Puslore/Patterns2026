from Src.Core.abstract_model import abstact_model


"""
Общий класс для наследования. Содержит стандартное определение: код, наименование
"""
class entity_model(abstact_model):
    __name:str = ""

    def __init__(self):
        super().__init__()

    """
    Наименование
    """
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value:str):
        self.__name = value.strip()

    def update_from(self, source):
        """Обновить состояние сущности данными из другого экземпляра."""
        super().update_from(source)
        self.name = source.name

  