from Src.Core.entity_model import entity_model

"""
Модель группы номенклатуры
"""
class group_model(entity_model):
    @classmethod
    def create(cls, name: str):
        result = cls()
        result.name = name
        return result

    @staticmethod
    def create_ingredients():
        return group_model.create("Ингредиенты")


    
    

    


    
