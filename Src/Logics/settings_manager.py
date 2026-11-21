from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
import json
import os
from Src.Models.settings_model import settings_model
from Src.Models.company_model import company_model
from Src.Core.common import common
from Src.Logics.convertor import convertor

"""
Менеджер для работы с настройками
"""
class settings_manager(abstract_manager):
    """Менеджер загрузки, сборки и хранения пользовательских настроек."""

    # Наименование файла по умолчанию
    __default_file_name:str = "settings.json"
    # Настройки
    __settings:settings_model
    # Загруженные сырые данные
    __data:dict = {}
    # Информация об ошибке при загрузке
    __inner_error:str = ""

    def __init__(self):
        """Создать менеджер с пустой моделью настроек."""
        self.__settings = self.__create_default_data()

    # Singletone
    def __new__(cls):
        """Вернуть единственный экземпляр менеджера."""
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance
  
    """
    Загрузить данные из файла и сформировать модель настроек.
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
            with open(full_file_name, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
        except Exception as ex:
            raise operation_exception(f"Ошибка при чтении файла {inner_file_name}: {ex}")

        worker = convertor()
        try:
            result = worker.deserialize(raw_data)
        except Exception as ex:
            raise operation_exception(f"Ошибка при десериализации файла {inner_file_name}: {ex}")

        if worker.is_error or result is None or not isinstance(result, settings_model):
            err = worker.error_text or "Десериализованный объект не является settings_model"
            raise operation_exception(f"Ошибка при загрузке настроек из {inner_file_name}: {err}")

        # Применяем результат только после успешного восстановления
        self.__data = raw_data
        self.__settings = result
        self.is_loaded = True
        return True

    """
    Вернуть текущую модель настроек.
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings

    """
    Обработать загруженные данные и заполнить модели настроек через общий механизм десериализации.
    """
    def build(self) -> bool:
        if len(self.__data) == 0:
            return False

        try:
            worker = convertor()
            result = worker.deserialize(self.__data)
            if worker.is_error or result is None or not isinstance(result, settings_model):
                self.__inner_error = worker.error_text or "Десериализованный объект не является settings_model"
                return False

            self.__settings = result
            return True
        except Exception as ex:
            self.__inner_error = str(ex)
            return False          


    """
    Создать настройки по умолчанию для первого запуска приложения.
    """
    def __create_default_data(self) -> settings_model:
        result = settings_model()

        company = company_model()
        company.bik = "044525225"
        company.inn = 7707083893
        company.corr_account = "30101810400000000225"
        company.name = " Сбербанка (Москва)"
        company.account = "40812810400000000225"

        result.company = company
        result.boss_name = "Иванов Иван Иванович"
        result.account_name = "Петров Петр Петрович"
        return result
