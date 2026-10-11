from Src.Core.entity_model import entity_model

"""
Модель группы номенклатуры
"""
class group_model(entity_model):
    """Группа, используемая для классификации номенклатуры."""

    @classmethod
    def create(cls, name: str):
        """Создать группу с заданным наименованием."""
        result = cls()
        result.name = name
        return result

    @staticmethod
    def create_ingredients():
        """Создать стандартную группу «Ингредиенты»."""
        return group_model.create("Ингредиенты")


    
    

    


    
