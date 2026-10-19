from Src.Core.entity_model import entity_model

"""
Модель группы номенклатуры
"""
class group_model(entity_model):

    def __init__(self):
       super().__init__()

    """
    Фабричный метод - создать группу по умолчанию
    """
    @staticmethod
    def create_default_group() -> "group_model":
        result = group_model()
        result.name = "Ингредиенты"

        return result


    
    

    


    
