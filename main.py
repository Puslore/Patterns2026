from pathlib import Path

from flask import Flask, Response

from Src.Core.validator import argument_exception
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.response_format_enum import response_format_enum


app = Flask(__name__)


class ambiguous_entity_error(LookupError):
    """Запрос по названию соответствует нескольким сущностям."""


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


def _find_entity(entity_type: str, identifier: str):
    """Найти доменную сущность по уникальному коду или названию."""
    key = _entity_type_aliases.get(entity_type.strip().casefold())
    if key is None:
        raise LookupError(f"Неизвестный тип сущности: {entity_type}")

    items = storage.data[key]
    normalized_identifier = identifier.strip().casefold()
    entity_by_code = next(
        (item for item in items
         if item.unique_code.casefold() == normalized_identifier),
        None,
    )
    if entity_by_code is not None:
        return entity_by_code

    entities_by_name = [
        item for item in items
        if item.name.strip().casefold() == normalized_identifier
    ]
    if len(entities_by_name) > 1:
        raise ambiguous_entity_error(
            f"Название «{identifier}» соответствует нескольким сущностям "
            f"типа {entity_type}; используйте уникальный код")
    if not entities_by_name:
        raise LookupError(
            f"Сущность типа {entity_type} с кодом или названием "
            f"«{identifier}» не найдена")
    return entities_by_name[0]


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


@app.errorhandler(ambiguous_entity_error)
def _ambiguous_entity(error):
    return Response(str(error), status=409, content_type="text/plain; charset=utf-8")


@app.get("/api/report/format/<response_format>/<entity_type>/<entity_identifier>")
def get_entity_report(response_format: str, entity_type: str, entity_identifier: str):
    """Вернуть отчет по коду или точному названию сущности."""
    entity = _find_entity(entity_type, entity_identifier)
    report = factory.create(response_format_enum.from_value(response_format))
    return _create_response(report.build(entity))


@app.get("/api/report/<entity_type>/<entity_identifier>")
def get_default_entity_report(entity_type: str, entity_identifier: str):
    """Вернуть отчет по коду или точному названию в формате из настроек."""
    entity = _find_entity(entity_type, entity_identifier)
    return _create_response(factory.create_default().build(entity))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
