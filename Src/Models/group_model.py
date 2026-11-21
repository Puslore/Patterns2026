from Src.Core.entity_model import entity_model
from Src.Core.validator import validator

"""
Модель группы номенклатуры
"""
class group_model(entity_model):
    """Группа, используемая для классификации номенклатуры."""

    __parent: "group_model" = None

    def __init__(self):
        """Инициализировать модель группы номенклатуры."""
        super().__init__()
        self.__parent = None

    @property
    def parent(self) -> "group_model":
        """Родительская группа (группа-владелец)."""
        return self.__parent

    @parent.setter
    def parent(self, value: "group_model") -> None:
        """Установить родительскую группу."""
        if value is not None:
            validator.validate(value, group_model)
        self.__parent = value

    @property
    def owner(self) -> "group_model":
        """Алиас для группы-владельца."""
        return self.__parent

    @owner.setter
    def owner(self, value: "group_model") -> None:
        """Установить группу-владельца."""
        self.parent = value

    @classmethod
    def create(cls, name: str) -> "group_model":
        """Создать группу с заданным наименованием."""
        result = cls()
        result.name = name
        return result

    @staticmethod
    def create_ingredients() -> "group_model":
        """Создать стандартную группу «Ингредиенты»."""
        return group_model.create("Ингредиенты")

    @staticmethod
    def create_default_group() -> "group_model":
        """Фабричный метод - создать группу по умолчанию."""
        return group_model.create_ingredients()

    def get_references(self) -> list:
        """Вернуть зависимости группы (родительскую группу-владельца)."""
        refs = super().get_references()
        if self.parent is not None:
            refs.append(self.parent)
        return refs

    def update_from(self, source):
        """Обновить состояние группы из валидированного объекта."""
        super().update_from(source)
        if hasattr(source, "parent"):
            self.parent = source.parent


    
    

    


    
