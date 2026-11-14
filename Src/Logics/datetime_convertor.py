from Src.Core.abstract_convertor import abstract_convertor
from datetime import datetime


"""
Конвертация даты
"""
class datetime_convertor(abstract_convertor):

    def __init__(self):
       super().__init__()
       
    """
    Выполнить сериализацию
    """
    def serialize(self, field: str,  object):

        super().serialize( field, object)

        if not isinstance(object, datetime):
          self.error_text = f"Некорректный тип данных передан для конвертации. Ожидается: datetime. Передан: {type(object)}"
          return None

        try:
            return { field: object.strftime('%Y-%m-%d %H:%M') }
        except Exception as ex:
            self.set_exception(ex)    


 
    """
    Выполнить десериализацию
    """
    def deserialize(self, source: dict ) -> object:
        pass