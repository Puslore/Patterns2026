
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