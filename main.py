from pathlib import Path

from flask import Flask, Response

from Src.Core.validator import argument_exception
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.response_format_enum import response_format_enum


app = Flask(__name__)

settings = settings_manager()
settings.load(str(Path(__file__).with_name("settings.json")))

storage = storage_manager(settings.settings)
storage.build()

factory = report_factory(settings.settings)

_entity_type_aliases = {
    "nomenclature": storage_manager.nomenclature_key(),
    "номенклатура": storage_manager.nomenclature_key(),
    "range": storage_manager.range_key(),
    "unit": storage_manager.range_key(),
    "единица измерения": storage_manager.range_key(),
    "recipe": storage_manager.recipe_key(),
    "рецепт": storage_manager.recipe_key(),
}


def _find_entity(entity_type: str, entity_code: str):
    """Найти доменную сущность по типу и уникальному коду."""
    key = _entity_type_aliases.get(entity_type.strip().casefold())
    if key is None:
        raise LookupError(f"Неизвестный тип сущности: {entity_type}")

    entity = next(
        (item for item in storage.data[key]
         if item.unique_code.casefold() == entity_code.strip().casefold()),
        None,
    )
    if entity is None:
        raise LookupError(f"Сущность типа {entity_type} с кодом {entity_code} не найдена")
    return entity


def _create_response(result):
    """Преобразовать результат форматировщика в HTTP-ответ."""
    headers = {}
    if result.filename is not None:
        headers["Content-Disposition"] = (
            f'attachment; filename="{result.filename}"'
        )
    return Response(result.content, content_type=result.content_type, headers=headers)


@app.errorhandler(argument_exception)
def _invalid_report_request(error):
    return Response(str(error), status=400, content_type="text/plain; charset=utf-8")


@app.errorhandler(LookupError)
def _entity_not_found(error):
    return Response(str(error), status=404, content_type="text/plain; charset=utf-8")


@app.get("/api/report/format/<response_format>/<entity_type>/<entity_code>")
def get_entity_report(response_format: str, entity_type: str, entity_code: str):
    """Вернуть отчет в явно заданном формате для сущности с указанным кодом."""
    entity = _find_entity(entity_type, entity_code)
    report = factory.create(response_format_enum.from_value(response_format))
    return _create_response(report.build(entity))


@app.get("/api/report/<entity_type>/<entity_code>")
def get_default_entity_report(entity_type: str, entity_code: str):
    """Вернуть отчет в формате из настроек приложения."""
    entity = _find_entity(entity_type, entity_code)
    return _create_response(factory.create_default().build(entity))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
