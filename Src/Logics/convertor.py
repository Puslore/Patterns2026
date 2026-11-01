from Src.Logics.convert_factory import convert_factory
from Src.Core.abstract_model import abstact_model
from typing import Any, Dict, Type

from Src.Core.validator import validator
from Src.Core.common import common


class convertor:
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
          return result


    """
    Десериализовать словарь в объект
    """
    def deserizlize(self, source: dict) -> object:
          pass



