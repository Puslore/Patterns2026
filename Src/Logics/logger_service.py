import csv
import io
from typing import List, Optional
from datetime import datetime

from Src.Core.abstract_observabile import abstract_observabile
from Src.Core.event_type import event_type
from Src.Core.validator import validator, argument_exception
from Src.Core.log_level_enum import log_level_enum
from Src.Models.log_model import log_model
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.prototype import prototype
from Src.Logics.observer import observer


class logger_service(abstract_observabile):
    """
    Сервис бизнес-логики для логирования операций, фильтрации и экспорта записей лога.
    Реализует шаблон 'Наблюдатель' (abstract_observabile) для подписки на события системы.
    """

    # Список записей логов
    __logs: List[log_model] = None

    # Реализация Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(logger_service, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
        Инициализировать сервис логирования и зарегистрировать его в шине observer.
        """
        super().__init__()
        if self.__logs is None:
            self.__logs = []
        observer.add(self)

    @property
    def logs(self) -> List[log_model]:
        """
        Получить копию текущего списка записей журнала.
        """
        return list(self.__logs)

    def clear(self) -> None:
        """
        Очистить журнал логов.
        """
        self.__logs.clear()

    def handler(self, event_types: str, params: object = None) -> None:
        """
        Обработчик событий от шины Наблюдателя (abstract_observabile).
        Автоматически формирует запись лога по типу события и переданным параметрам.
        """
        subsystem = "general"
        level = log_level_enum.INFO
        message = ""

        # Специфические настройки по типу события по умолчанию
        if event_types == event_type.load_settings():
            subsystem = "settings_manager"
            message = "Загружены настройки приложения"
        elif event_types == event_type.change_settings():
            subsystem = "settings_manager"
            message = "Изменены параметры настроек приложения"
        elif event_types == event_type.warehouse_operation():
            subsystem = "storage_manager"
            message = "Выполнена складская операция"
        elif event_types in (event_type.create_entity(), event_type.update_entity(), event_type.delete_entity()):
            subsystem = "storage_service"
            message = f"Выполнена CRUD операция: {event_types}"
        elif event_types in (event_type.web_request(), event_type.web_response()):
            subsystem = "web_api"
            message = f"Событие Web API: {event_types}"

        # Извлечение параметров, если переданы
        if isinstance(params, dict):
            subsystem = params.get("subsystem", subsystem)
            level = params.get("level", level)
            msg_param = params.get("message")
            if msg_param:
                message = str(msg_param)
        elif isinstance(params, str) and params.strip():
            message = f"{message} ({params})" if message else params

        if not message:
            message = f"Событие: {event_types}"

        self.log(subsystem=subsystem, level=level, message=message)

    def log(self, subsystem: str, level: object, message: str) -> log_model:
        """
        Записать новое сообщение в журнал логов.
        """
        validator.validate(subsystem, str)
        validator.validate(message, str)

        entry = log_model.create(subsystem=subsystem, level=level, message=message)
        self.__logs.append(entry)
        return entry

    def info(self, subsystem: str, message: str) -> log_model:
        """
        Записать информационное сообщение (INFO).
        """
        return self.log(subsystem, log_level_enum.INFO, message)

    def error(self, subsystem: str, message: str) -> log_model:
        """
        Записать сообщение об ошибке (ERROR).
        """
        return self.log(subsystem, log_level_enum.ERROR, message)

    def debug(self, subsystem: str, message: str) -> log_model:
        """
        Записать отладочное сообщение (DEBUG).
        """
        return self.log(subsystem, log_level_enum.DEBUG, message)

    def get_logs(
        self,
        filter_data: Optional[dict] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> List[log_model]:
        """
        Получить отфильтрованный и отсортированный список записей лога с помощью Прототипа.
        """
        items = list(self.__logs)

        # 1. Фильтрация через существующий prototype
        if filter_data and isinstance(filter_data, dict):
            dto = filter_dto().from_dict(filter_data)
            items = prototype(items).clone(dto).data

        # 2. Сортировка по указанному полю
        if sort_by:
            valid_fields = ("period", "subsystem", "level", "message", "unique_code")
            target_field = sort_by.strip().lower()
            if target_field not in valid_fields:
                raise argument_exception(
                    f"Недопустимое поле для сортировки: {sort_by}. Допустимые: {', '.join(valid_fields)}"
                )

            reverse = str(sort_order).strip().lower() in ("desc", "reverse", "2")

            def sort_key(item: log_model):
                val = getattr(item, target_field, None)
                if val is None:
                    return ""
                return val

            items = sorted(items, key=sort_key, reverse=reverse)

        return items

    def export(self, items: List[log_model], format_type: str) -> report_result_dto:
        """
        Экспортировать записи лога в указанном формате: TXT, CSV или MARKDOWN.
        """
        validator.validate(items, list)
        validator.validate(format_type, str)

        fmt = format_type.strip().upper()
        res = report_result_dto()

        if fmt == "TXT":
            lines = [f"{'Период':<20} | {'Название подсистемы':<20} | {'Тип':<7} | {'Сообщение'}"]
            lines.append("-" * 80)
            for item in items:
                period_str = item.period.strftime("%Y-%m-%d %H:%M:%S") if item.period else ""
                lines.append(f"{period_str:<20} | {item.subsystem:<20} | {item.level:<7} | {item.message}")
            res.text = "\n".join(lines)
            res.format = "text/plain"
            return res

        if fmt == "CSV":
            output = io.StringIO()
            writer = csv.writer(output, delimiter=";")
            writer.writerow(["Период", "Название подсистемы", "Тип сообщения", "Сообщение"])
            for item in items:
                period_str = item.period.strftime("%Y-%m-%d %H:%M:%S") if item.period else ""
                writer.writerow([period_str, item.subsystem, item.level, item.message])
            res.text = output.getvalue()
            res.format = "text/csv"
            return res

        if fmt in ("MARKDOWN", "MD"):
            lines = [
                "| Период | Название подсистемы | Тип сообщения | Сообщение |",
                "| --- | --- | --- | --- |",
            ]
            for item in items:
                period_str = item.period.strftime("%Y-%m-%d %H:%M:%S") if item.period else ""
                clean_msg = item.message.replace("|", "\\|")
                lines.append(f"| {period_str} | {item.subsystem} | {item.level} | {clean_msg} |")
            res.text = "\n".join(lines)
            res.format = "text/markdown"
            return res

        raise argument_exception(f"Неподдерживаемый формат экспорта: {format_type}. Допустимы: TXT, CSV, MARKDOWN")
