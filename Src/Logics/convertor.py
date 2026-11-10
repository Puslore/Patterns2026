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
      convertor = self.__factory.create( source )
      result = convertor.serialize( "result", source )
      if convertor.is_error:
        self.error_text +=  f"Ошибка при выполнении сериализации!\n{convertor.error_text}"
            
      return result


    """
    Десериализовать словарь в объект
    """
    def deserialize(self, source: dict) -> object:
      validator.validate (source, dict)
      if len(source.keys()) == 0:
          raise operation_exception("Для десериализации требуется заполненный словарь!")
          
      convertor = self.__factory.create( source )
      result = convertor.deserialize( source )
      if convertor.is_error:
          self.error_text +=  f"Ошибка при выполнении десериализации!\n{convertor.error_text}"
      
      return result



