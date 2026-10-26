from Src.Core.abstract_convertor import abstract_convertor

"""
Конвертация простого объекта
"""
class basic_convertor(abstract_convertor):

   def __init__(self):
       super().__init__()

   """
   Выполнить сериализацию
   """ 
   def serialize(self, field: str, object:any) -> dict:
      super().serialize( field, object)

      if not isinstance(object, (int, str, bool, float)):
          self.error_text = f"Некорректный тип данных передан для конвертации. Ожидается: (int, str, bool). Передан: {type(object)}"
          return None

      try:
            return { field: object }
      except Exception as ex:
            self.set_exception(ex)  

      return None   


   """
   Выполнить десериализацию
   """
   def deserialize(self, source: dict ) -> object:
        pass