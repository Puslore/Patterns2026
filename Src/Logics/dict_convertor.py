from Src.Core.abstract_convertor import abstract_convertor

"""
Конвертация словаря
"""
class dict_convertor(abstract_convertor):

    def __init__(self):
        super().__init__()

    """
    Выполнить сериализацию
    """ 
    def serialize(self, field: str, object:any) -> dict:
       super().serialize( field, object)
       pass

    """
    Выполнить десериализацию
    """
    def deserialize(self, source: dict ) -> object:
        super().deserialize(source)
        pass