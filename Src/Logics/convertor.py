from Src.Logics.convert_factory import convert_factory
from Src.Core.validator import validator, operation_exception
from Src.Core.abstract_error import abstract_error

class convertor(abstract_error):
    # Фабрика для подбора конвертора
    __factory: convert_factory = None

    def __init__(self):
        self.__factory = convert_factory()

    
    # Singletone
    def __new__(cls):
          if not hasattr(cls, 'instance'):
                  cls.instance = super(convertor, cls).__new__(cls)
          return cls.instance 

    """
    Сериализовать объект в словарь
    """
    def serialize(self, source: any ) -> dict:
      self.clear_error()
      conv = self.__factory.create( source )
      if hasattr(conv, "clear_error"):
          conv.clear_error()
      result = conv.serialize( "result", source )
      if conv.is_error:
        self.error_text +=  f"Ошибка при выполнении сериализации!\n{conv.error_text}"
            
      return result


    """
    Десериализовать словарь в объект
    """
    def deserialize(self, source: dict) -> object:
      self.clear_error()
      validator.validate (source, dict)
      if len(source.keys()) == 0:
          raise operation_exception("Для десериализации требуется заполненный словарь!")
          
      conv = self.__factory.create( source )
      if hasattr(conv, "clear_error"):
          conv.clear_error()
      result = conv.deserialize( source )
      if conv.is_error:
          self.error_text +=  f"Ошибка при выполнении десериализации!\n{conv.error_text}"
      
      return result



