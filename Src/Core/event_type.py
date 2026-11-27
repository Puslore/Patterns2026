"""
Типы сообщений
"""
class event_type:

    """
    Изменены настройки
    """
    @staticmethod
    def change_settings() -> str:
        return "change_settings"

    """
    Загружены настройки
    """
    @staticmethod
    def load_settings() -> str:
        return "load_settings"

    """
    Создание доменной сущности (CRUD)
    """
    @staticmethod
    def create_entity() -> str:
        return "create_entity"

    """
    Обновление доменной сущности (CRUD)
    """
    @staticmethod
    def update_entity() -> str:
        return "update_entity"

    """
    Удаление доменной сущности (CRUD)
    """
    @staticmethod
    def delete_entity() -> str:
        return "delete_entity"

    """
    Складская операция (поступление / списание / транзакция)
    """
    @staticmethod
    def warehouse_operation() -> str:
        return "warehouse_operation"

    """
    Вызов Web-метода (HTTP запрос)
    """
    @staticmethod
    def web_request() -> str:
        return "web_request"

    """
    Ответ Web-метода (HTTP ответ)
    """
    @staticmethod
    def web_response() -> str:
        return "web_response"
