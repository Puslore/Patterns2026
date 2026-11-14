from Src.Core.entity_model import entity_model

"""
Модель группы номенклатуры
"""
class group_model(entity_model):
    """Группа, используемая для классификации номенклатуры."""

    def __init__(self):
        """Инициализировать модель группы номенклатуры."""
        super().__init__()

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


    
    

    


    
