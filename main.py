import connexion
from flask import request, jsonify
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.storage_service import storage_service
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.convertor import convertor
from Src.Core.validator import (
    operation_exception,
    argument_exception,
    not_found_exception,
    conflict_exception,
)

# Создание приложения Connexion
api = connexion.FlaskApp(__name__, specification_dir="./")

# Настройки приложения
app_settings_manager = settings_manager()
app_settings_manager.load()

# Хранилище данных
app_storage_manager = storage_manager(app_settings_manager.settings)
app_storage_manager.build()

# Сервисный слой
app_storage_service = storage_service(app_storage_manager)

# Конвертор для сериализации
worker = convertor()


def _serialize_item(item):
    """Сериализовать объект доменной модели в словарь для JSON-ответа."""
    if item is None:
        return None
    res = worker.serialize(item)
    return res.get("result", res)


def get_default_report(entity: str = None, unique_code: str = None):
    """Получить отчет в формате по умолчанию."""
    try:
        key = entity or request.args.get("entity")
        code = unique_code or request.args.get("unique_code")

        if not key or not code:
            return (
                jsonify({"detail": "Отсутствуют обязательные параметры entity или unique_code"}),
                400,
            )

        item = app_storage_service.get_by_code(key, code)

        factory = report_factory(app_settings_manager.settings)
        report_builder = factory.create_default()
        result = report_builder().build(item)

        return result.text, 200, {"Content-Type": result.format}
    except not_found_exception as ex:
        return jsonify({"detail": str(ex)}), 404
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


def get_entities():
    """Получить список доменных сущностей (ключей и их описаний)."""
    try:
        source = app_storage_manager.domains()
        result = worker.serialize(source)
        return jsonify(result), 200, {"Content-Type": "application/json"}
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


def get_report_formats():
    """Получить список всех форматов для построения отчетов из перечисления."""
    try:
        formats = [{"name": item.name, "value": item.value} for item in report_type_enum]
        return jsonify(formats), 200, {"Content-Type": "application/json"}
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


def get_report_formats_alias():
    """Алиас для получения форматов отчетов по старому адресу."""
    return get_report_formats()


def get_all_entities(entity: str):
    """Получить список всех объектов сущности указанного типа."""
    try:
        items = app_storage_service.get_all(entity)
        result = [_serialize_item(item) for item in items]
        return jsonify(result), 200, {"Content-Type": "application/json"}
    except not_found_exception as ex:
        return jsonify({"detail": str(ex)}), 404
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


def get_entity_by_id(entity: str, unique_code: str):
    """Получить один объект сущности по ее типу и уникальному коду."""
    try:
        item = app_storage_service.get_by_code(entity, unique_code)
        return jsonify(_serialize_item(item)), 200, {"Content-Type": "application/json"}
    except not_found_exception as ex:
        return jsonify({"detail": str(ex)}), 404
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


def create_entity(entity: str):
    """Создать новую доменную сущность."""
    try:
        payload = request.get_json(silent=True)
        if not payload or not isinstance(payload, dict):
            return (
                jsonify({"detail": "Отсутствует тело запроса или передан некорректный JSON"}),
                400,
            )

        item = app_storage_service.create(entity, payload)
        return jsonify(_serialize_item(item)), 201, {"Content-Type": "application/json"}
    except not_found_exception as ex:
        return jsonify({"detail": str(ex)}), 404
    except conflict_exception as ex:
        return jsonify({"detail": str(ex)}), 409
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


def update_entity(entity: str, unique_code: str):
    """Обновить существующую доменную сущность."""
    try:
        payload = request.get_json(silent=True)
        if not payload or not isinstance(payload, dict):
            return (
                jsonify({"detail": "Отсутствует тело запроса или передан некорректный JSON"}),
                400,
            )

        item = app_storage_service.update(entity, unique_code, payload)
        return jsonify(_serialize_item(item)), 200, {"Content-Type": "application/json"}
    except not_found_exception as ex:
        return jsonify({"detail": str(ex)}), 404
    except conflict_exception as ex:
        return jsonify({"detail": str(ex)}), 409
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


def delete_entity(entity: str, unique_code: str):
    """Удалить доменную сущность."""
    try:
        app_storage_service.delete(entity, unique_code)
        return jsonify({"result": True}), 200, {"Content-Type": "application/json"}
    except not_found_exception as ex:
        return jsonify({"detail": str(ex)}), 404
    except conflict_exception as ex:
        return jsonify({"detail": str(ex)}), 409
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


def filter_entities(entity: str):
    """Отфильтровать доменные сущности указанного типа с помощью DTO модели фильтрации."""
    try:
        payload = request.get_json(silent=True)
        if payload is None or not isinstance(payload, dict):
            return (
                jsonify({"detail": "Отсутствует тело запроса или передан некорректный JSON"}),
                400,
            )

        items = app_storage_service.filter_entities(entity, payload)
        result = [_serialize_item(item) for item in items]
        return jsonify(result), 200, {"Content-Type": "application/json"}
    except not_found_exception as ex:
        return jsonify({"detail": str(ex)}), 404
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


def get_osv_report():
    """Сформировать оборотно-сальдовую ведомость (ОСВ) с учетом фильтрации через Прототип."""
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            payload = {}
        elif not isinstance(payload, dict):
            return (
                jsonify({"detail": "Тело запроса должно быть JSON-объектом"}),
                400,
            )

        osv_data = app_storage_service.build_osv(payload)
        return jsonify(osv_data), 200, {"Content-Type": "application/json"}
    except not_found_exception as ex:
        return jsonify({"detail": str(ex)}), 404
    except (operation_exception, argument_exception) as ex:
        return jsonify({"detail": str(ex)}), 400
    except Exception as ex:
        return jsonify({"detail": f"Ошибка: {ex}"}), 500


# Регистрация явных алиасов маршрутов на уровне Flask
@api.route("/api/filter/<entity>", methods=["POST"])
def filter_entities_alias(entity: str):
    return filter_entities(entity)


@api.route("/api/osv", methods=["POST"])
def get_osv_report_alias():
    return get_osv_report()


# Подключаем спецификацию OpenAPI для регистрации маршрутов
api.add_api("openapi.yaml")

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8080)
