from Src.Models.company_model import company_model
from Src.Logics.text_report import text_report
from Src.Models.settings_model import settings_model
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report
from Src.Models.range_model import range_model

"""
Проверить метод build класса text_report
"""
def test_not_empty_text_report_build():
    # Подготовка
    model = company_model()
    report = text_report()

    # Действие
    result = report.build( model )

    # Проверка
    print(result.text )
    assert result.text != ""


"""
Проверить метод build класса csv_report
"""
def test_not_empty_csv_report_build():
    # Подготовка
    model = range_model().create_killogramm()
    report = csv_report()

    # Действие
    result = report.build( model )

    # Проверка
    print(result.text )
    assert result.text != ""

"""
Проверить метод build класса csv_report
"""
def test_not_empty_markdowm_report_build():
    # Подготовка
    model = range_model().create_killogramm()
    report = markdown_report()

    # Действие
    result = report.build( model )

    # Проверка
    print(result.text )
    assert result.text != ""    


"""
Проверить работу абстрактной фабрики
"""
def test_not_empty_report_factory_create_default():
    # Подготовка
    settings =    settings_model()
    settings.default_report_type =  report_type_enum.TXT.value
    factory = report_factory(settings)
    model = company_model()

    # Действие
    report_type = factory.create_default()
    result = report_type().build( model )

    # Проверки
    assert result.text != ""


