from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
import json
import os
from Src.Models.settings_model import settings_model
from Src.Models.company_model import company_model
from Src.Core.common import common

"""
Менеджер для работы с настройками
"""
class settings_manager(abstract_manager):
    # Наименование файла по умолчанию
    __default_file_name:str = "settings.json"
    # Настройки
    __settings:settings_model = None
    # Загруженные сырые данные
    __data:list = [] 

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

        # Определим название фала
        inner_file_name = file_name if file_name.strip() != "" else self.__default_file_name
        validator.validate(inner_file_name, str)

        # Дополним имя с учетом текщего каталога
        full_file_name = os.path.abspath(inner_file_name)        
        if not os.path.exists(full_file_name):
            raise operation_exception(f'Не найден указанный файл {full_file_name}')

        try:
            with open(full_file_name, "r") as file:
                self.__data = json.load(file)
                self.__is_loaded = self.build()
                if not self.__is_loaded:
                    self.__settings = self.__create_default_data() 
        except Exception as ex:
            raise  operation_exception(f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}")      

    """
    Модель настроек
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings

    """
    Обработать загруженные данные
    """
    def build(self) -> bool:
        if len(self.__data) == 0:
              return False

        try: 
            # Загружаем данные по организации
            company = company_model()
            fields = common.get_fields(company, True)
            for field in fields:
                key = f"company_{field}"
                if key  in self.__data.keys():
                    setattr( company, field, self.__data[key])

            # Загружаем данные по настройкам
            fields = common.get_fields(self.__settings, True)
            for field in fields:
                key = f"{field}"
                if key in self.__data.keys():
                    setattr( company, field, self.__data[key])

            return True        
        except:
            return False          


    """
    Сформировать настройки по умолчанию
    """
    def __create_default_data(self) -> settings_model:
        result = settings_model()

        company = company_model()
        company.bik = "044525225"
        company.inn = "7707083893"
        company.corr_account = "30101810400000000225"
        company.name = " Сбербанка (Москва)"
        company.account = "40812810400000000225"

        result.company = company
        result.boss_name = "Воловиков Александр Сергеевич"
        result.account_name = "Балахчи Анна Георгиевна"

   
