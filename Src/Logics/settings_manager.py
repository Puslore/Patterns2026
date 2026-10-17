from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception, argument_exception
import json
import os
from Src.Models.settings_model import settings_model
from Src.Models.company_model import company_model
from Src.Core.common import common
from Src.Models.response_format_enum import response_format_enum

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

        if not isinstance(file_name, str):
            raise operation_exception("Имя файла настроек должно быть строкой")
        inner_file_name = file_name.strip() or self.__default_file_name
        validator.validate(inner_file_name, str)

        # Дополним имя с учетом текщего каталога
        full_file_name = os.path.abspath(inner_file_name)        
        if not os.path.exists(full_file_name):
            raise operation_exception(f'Не найден указанный файл {full_file_name}')

        try:
            with open(full_file_name, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise operation_exception("Файл настроек должен содержать JSON-объект")
            self.__data = data
            self.is_loaded = self.build()
            if not self.is_loaded:
                self.__settings = self.__create_default_data()
        except operation_exception:
            raise
        except (OSError, json.JSONDecodeError, ValueError, TypeError,
                argument_exception) as ex:
            raise operation_exception(
                f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}") from ex

    """
    Вернуть текущую модель настроек.
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings

    """
    Обработать загруженные данные и заполнить модели настроек.
    """
    def build(self) -> bool:
        if len(self.__data) == 0:
              return False

        result = self.__create_default_data()
        company = result.company
        for field in common.get_fields(company, True):
            key = f"company_{field}"
            if key in self.__data:
                setattr(company, field, self.__data[key])

        for field in ("boss_name", "account_name", "first_start", "response_format"):
            if field not in self.__data:
                continue
            value = self.__data[field]
            if field == "response_format":
                value = response_format_enum.from_value(value)
            setattr(result, field, value)

        self.__settings = result
        return True


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
