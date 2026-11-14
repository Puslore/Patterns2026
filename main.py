from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
import connexion
from Src.Logics.convertor import convertor
from Src.Core.validator import operation_exception, argument_exception
from flask import request, jsonify

# Создание приложения Connexion
api = connexion.FlaskApp(__name__, specification_dir="./")

# Настройки приложения
app_settings_manager = settings_manager()
app_settings_manager.load()

# Хранилище данных
app_storage_manager = storage_manager(app_settings_manager.settings)
app_storage_manager.build()

# Конвертор
worker = convertor()

ENTITY_DTO_MAP = {
    "range_model": "Src.Dtos.range_dto.range_dto",
    "group_model": "Src.Dtos.group_dto.group_dto",
    "nomenclature_model": "Src.Dtos.nomenclature_dto.nomenclature_dto",
    "storage_model": "Src.Dtos.storage_dto.storage_dto",
    "receipt_model": "Src.Dtos.receipt_dto.receipt_dto",
    "company_model": "Src.Dtos.company_dto.company_dto",
    "ingredient_model": "Src.Dtos.ingredient_dto.ingredient_dto",
}


def _serialize_item(item):
    """Сериализовать один объект доменной модели в словарь."""
    if item is None:
        return None
    res = worker.serialize(item)
    return res.get("result", res)


def _deserialize_payload(entity: str, payload: dict):
    """Десериализовать словарь в объект доменной модели через общий механизм десериализации."""
    if not isinstance(payload, dict):
        raise argument_exception("Тело запроса должно быть JSON-объектом!")

    data = dict(payload)
    if "type" not in data and entity in ENTITY_DTO_MAP:
        data["type"] = ENTITY_DTO_MAP[entity]

    item = worker.deserialize(data)
    if worker.is_error or item is None:
        err = worker.error_text or "Ошибка десериализации данных"
        raise operation_exception(err)
    return item


"""
Получить отчет в формате по умолчанию
"""
@api.route("/api/get_default_report", methods=["GET"])
def get_default_report():
    try:
        key = request.args.get('entity')
        unique_code = request.args.get('unique_code')

        if not key or not unique_code:
            return jsonify({"detail": "Отсутствуют обязательные параметры entity или unique_code"}), 400

        if key not in app_storage_manager.data:
            return jsonify({"detail": f"Коллекция сущностей '{key}' не найдена"}), 404

        items = app_storage_manager.data[key]
        item = next((obj for obj in items if hasattr(obj, 'unique_code') and obj.unique_code == unique_code), None)
        if item is None:
            return jsonify({"detail": f"Объект с кодом '{unique_code}' не найден"}), 404

        factory = report_factory(app_settings_manager.settings)
        report_type = factory.create_default()
        result = report_type().build(item)

        return result.text, 200, {'Content-Type': result.format}
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


"""
Получить список доменных сущностей
"""
@api.route("/api/get_entities", methods=["GET"])
def get_entities():
    try:
        source = app_storage_manager.domains()
        result = worker.serialize(source)
        return jsonify(result), 200, {'Content-Type': 'application/json'}
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


"""
Получить список всех форматов для построения отчетов
"""
@api.route("/api/reports/formats", methods=["GET"])
@api.route("/api/get_report_formats", methods=["GET"])
def get_report_formats():
    try:
        formats = app_storage_manager.get_report_formats()
        return jsonify(formats), 200, {'Content-Type': 'application/json'}
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


"""
Получить список всех объектов сущности указанного типа
"""
@api.route("/api/entity/<entity>", methods=["GET"])
def get_all_entities(entity: str):
    try:
        if entity not in app_storage_manager.data:
            return jsonify({"detail": f"Тип сущности '{entity}' не поддерживается"}), 404

        items = app_storage_manager.data[entity]
        result = [_serialize_item(item) for item in items]
        return jsonify(result), 200, {'Content-Type': 'application/json'}
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


"""
Получить один объект сущности по ее типу и уникальному коду
"""
@api.route("/api/entity/<entity>/<unique_code>", methods=["GET"])
def get_entity_by_id(entity: str, unique_code: str):
    try:
        if entity not in app_storage_manager.data:
            return jsonify({"detail": f"Тип сущности '{entity}' не поддерживается"}), 404

        item = app_storage_manager.get_item(entity, unique_code)
        if item is None:
            return jsonify({"detail": f"Сущность с кодом '{unique_code}' не найдена"}), 404

        return jsonify(_serialize_item(item)), 200, {'Content-Type': 'application/json'}
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


"""
Создать новую доменную сущность
"""
@api.route("/api/entity/<entity>", methods=["POST"])
def create_entity(entity: str):
    try:
        if entity not in app_storage_manager.data:
            return jsonify({"detail": f"Тип сущности '{entity}' не поддерживается"}), 404

        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({"detail": "Отсутствует тело запроса или передан некорректный JSON"}), 400

        item = _deserialize_payload(entity, payload)
        app_storage_manager.add_item(entity, item)
        return jsonify(_serialize_item(item)), 201, {'Content-Type': 'application/json'}
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


"""
Обновить существующую доменную сущность
"""
@api.route("/api/entity/<entity>/<unique_code>", methods=["PUT"])
def update_entity(entity: str, unique_code: str):
    try:
        if entity not in app_storage_manager.data:
            return jsonify({"detail": f"Тип сущности '{entity}' не поддерживается"}), 404

        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({"detail": "Отсутствует тело запроса или передан некорректный JSON"}), 400

        data = dict(payload)
        if "unique_code" not in data or not data["unique_code"]:
            data["unique_code"] = unique_code

        item = _deserialize_payload(entity, data)
        updated = app_storage_manager.update_item(entity, unique_code, item)
        return jsonify(_serialize_item(updated)), 200, {'Content-Type': 'application/json'}
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


"""
Удалить доменную сущность
"""
@api.route("/api/entity/<entity>/<unique_code>", methods=["DELETE"])
def delete_entity(entity: str, unique_code: str):
    try:
        if entity not in app_storage_manager.data:
            return jsonify({"detail": f"Тип сущности '{entity}' не поддерживается"}), 404

        app_storage_manager.delete_item(entity, unique_code)
        return jsonify({"result": True}), 200, {'Content-Type': 'application/json'}
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


# Подключаем спецификацию OpenAPI
api.add_api('openapi.yaml')

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8080)
