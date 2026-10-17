import csv
from io import StringIO
from xml.etree import ElementTree

import pytest

from Src.Core.validator import argument_exception
from Src.Logics.report_factory import report_factory
from Src.Models.recipe_model import recipe_model
from Src.Models.response_format_enum import response_format_enum
from Src.Models.settings_model import settings_model


@pytest.mark.parametrize("response_format", list(response_format_enum))
def test_report_formats_include_recipe_composition(response_format):
    recipe = recipe_model.create_borsch()
    result = report_factory().create(response_format).build(recipe)

    content = result.content.decode("utf-8") if isinstance(result.content, bytes) else result.content
    assert "Борщ столичный" in content
    assert "Пассеровка свекольная" in content
    assert "Свёкла" in content
    assert "gross_weight_grams" in content

    if response_format in (response_format_enum.CSV, response_format_enum.MARKDOWN):
        assert isinstance(result.content, bytes)
        assert result.filename is not None
    else:
        assert isinstance(result.content, str)
        assert result.filename is None

    if response_format is response_format_enum.XML:
        root = ElementTree.fromstring(result.content)
        assert root.findtext("./entity/name") == "Борщ столичный"
        assert root.findtext(".//item/name") == "Пассеровка свекольная"
    elif response_format is response_format_enum.CSV:
        rows = list(csv.reader(StringIO(content)))
        assert rows[0] == ["Поле", "Значение"]
        assert any(row[1] == "Борщ столичный" for row in rows[1:])
    elif response_format is response_format_enum.HTML:
        assert "<!doctype html>" in content
        assert "<pre>" in content


def test_report_factory_create_default_uses_settings_format():
    settings = settings_model()
    settings.response_format = response_format_enum.MARKDOWN

    report = report_factory(settings).create_default()

    assert report.filename == "report.md"


def test_report_factory_create_default_accepts_format_override():
    factory = report_factory(settings_model())

    report = factory.create_default("XML")

    assert report.content_type == "application/xml; charset=utf-8"


def test_settings_model_rejects_non_enum_response_format():
    settings = settings_model()

    with pytest.raises(argument_exception):
        settings.response_format = "CSV"
