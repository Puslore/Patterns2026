from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
import json
from Src.Models.settings_model import settings_model

"""
Менеджер для работы с настройками
"""
class settings_manager(abstract_manager):
    __default_file_name:str = "settings.json"
    __settings:settings_model = None

    def __init__(self):
        self.__settings = settings_model()

    # Singletone
    def __new__(cls):
          if not hasattr(cls, 'instance'):
                  cls.instance = super(settings_manager, cls).__new__(cls)
          return cls.instance 
  
    """
    Загрузка данных
    """
    def load(self, file_name:str = ""):
        inner_file_name = file_name if file_name.strip() != "" else self.__default_file_name
        validator.validate(inner_file_name, str)

        try:
            with open(inner_file_name, "r") as file:
                self.__data = json.load(file)
                self.__is_loaded = self.convert()
        except Exception as ex:
            raise  operation_exception(f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}")      

    """
    Модель настроек
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings
