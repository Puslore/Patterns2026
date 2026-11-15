from Src.Core.entity_model import entity_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.validator import validator

"""
Модель номенклатуры
"""
class nomenclature_model(entity_model):
    __group: group_model = None
    __range: range_model = None

    def __init__(self):
        super().__init__()
   
    """
    Группа номенклатуры
    """
    @property
    def group(self) -> group_model:
        return self.__group

    @group.setter
    def group(self, value: group_model) -> None:
        validator.validate(value, group_model)
        self.__group = value    

    """
    Единица измерения
    """
    @property
    def range(self) -> range_model:
        return self.__range
    
    @range.setter
    def range(self, value: range_model) -> None:
        validator.validate(value, range_model)
        self.__range = value

    def get_references(self) -> list:
        """Вернуть зависимости номенклатуры (группа и единица измерения)."""
        refs = super().get_references()
        if self.group is not None:
            refs.append(self.group)
        if self.range is not None:
            refs.append(self.range)
        return refs

    def update_from(self, source):
        """Обновить состояние номенклатуры из валидированного объекта."""
        super().update_from(source)
        self.group = source.group
        self.range = source.range

    @staticmethod
    def create_ingredient(name: str, group: group_model, unit: range_model) -> nomenclature_model:
        """Создать номенклатуру ингредиента с группой и единицей измерения."""
        result = nomenclature_model()
        result.name = name
        result.group = group
        result.range = unit
        return result