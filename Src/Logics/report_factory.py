from Src.Core.abstract_report import abstract_report
from Src.Core.validator import argument_exception, validator
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.response_format_enum import response_format_enum
from Src.Models.settings_model import settings_model


class report_factory:
    """Создавать форматировщики отчетов по явному или настроенному формату."""

    def __init__(self, settings: settings_model = None):
        if settings is None:
            settings = settings_model()
        validator.validate(settings, settings_model)
        self.__settings = settings
        self.__mapping = {
            response_format_enum.CSV: csv_report,
            response_format_enum.MARKDOWN: markdown_report,
            response_format_enum.XML: xml_report,
            response_format_enum.TXT: text_report,
            response_format_enum.HTML: html_report,
        }

    @property
    def settings(self) -> settings_model:
        return self.__settings

    @settings.setter
    def settings(self, value: settings_model) -> None:
        validator.validate(value, settings_model)
        self.__settings = value

    def create(self, response_format: response_format_enum) -> abstract_report:
        """Создать форматировщик указанного формата."""
        selected_format = response_format_enum.from_value(response_format)
        return self.__mapping[selected_format]()

    def create_default(self, response_format=None) -> abstract_report:
        """Создать форматировщик из настроек с необязательным переопределением."""
        selected_format = (self.__settings.response_format if response_format is None
                           else response_format_enum.from_value(response_format))
        if not isinstance(selected_format, response_format_enum):
            raise argument_exception("В настройках задан некорректный формат отчета")
        return self.__mapping[selected_format]()
