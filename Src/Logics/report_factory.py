from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.text_report import text_report
from Src.Core.validator import argument_exception
from Src.Models.settings_model import settings_model
from Src.Core.validator import validator
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report


"""
Реализация фабрики для построения отчетов
"""
class report_factory(abstract_report_factory):
    # Маппинг тип отчета и его реализация
    __mapping:dict[report_type_enum, abstract_report] = {}
    # Иньекция настроек
    __settings:settings_model = None
    # Кеш
    __instance = None

    def __init__(self, settings:settings_model):
        # Инициализация сопоставления
        self.__mapping[ report_type_enum.TXT ] = text_report
        self.__mapping[ report_type_enum.CSV] = csv_report
        self.__mapping[ report_type_enum.MARKDOWN ] = markdown_report

        validator.validate(settings, settings_model)
        self.__settings = settings

    # Singletone
    def __new__(cls, settings: settings_model): 
        if cls.__instance is None: 
            cls.__instance = super(report_factory, cls).__new__(cls) 
        return cls.__instance

    """
    Выбрать нужный построитель отчета и вернуть его инстанс
    """
    def create(self, report_type: report_type_enum) -> abstract_report:
        if report_type not in self.__mapping.keys():
            raise argument_exception(f"Указанный тип отчета {report_type} не реалилизован!")

        return self.__mapping[ report_type ]

    """
    Выбрать нужный построитель отчета по умолчанию и вернуть его инстанс
    """
    def create_default(self) -> abstract_report:
        return self.create( self.__settings.default_report_type )


    """
    Текущие настройки
    """
    @property
    def settings(self) -> settings_model:
        return self.__settings

