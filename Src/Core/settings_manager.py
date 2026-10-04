from typing import Optional

from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception


class settings_manager(abstract_manager):
    """
    Менеджер настроек приложения.

    Хранит плоское хранилище настроек `ключ -> значение` и умеет:
        - задавать / читать настройки (get_setting / set_setting);
        - преобразовывать словарь настроек в типизированный объект
          по схеме (метод convert).

    Схема конвертации (`schema`) - словарь вида:
        { '<имя поля результата>': ('<имя ключа настройки>', <тип>) }

    Правила:
        - Ключи настроек - непустые строки; значения - любые объекты.
        - При конвертации отсутствующий ключ либо значение не по умолчанию
          заполняются default_value.
        - Если для поля указан тип, значение приводится к этому типу;
          при невозможности приведения выбрасывается arguments_exception.
    """

    # Значение настройки по умолчанию, используется при отсутствии ключа в хранилище.
    _default_value: object = None

    # Внутреннее хранилище настроек: ключ настройки -> значение.
    _settings: dict[str, object]

    def __init__(self, settings: Optional[dict[str, object]] = None,
                 default_value: object = None) -> None:
        """
        Инициализация менеджера настроек.
        :param settings: Необязательный начальный словарь настроек
        :param default_value: Необязательное значение настроек по умолчанию
        """
        self._settings = {}
        self.default_value = default_value
        if settings is not None:
            for key, value in settings.items():
                self.set_setting(key, value)

    @property
    def default_value(self) -> object:
        """
        Возвращает значение настроек по умолчанию.
        """
        return self._default_value

    @default_value.setter
    def default_value(self, value: object) -> None:
        """
        Установка значения настроек по умолчанию (любое, включая None).
        """
        self._default_value = value

    @property
    def settings(self) -> dict[str, object]:
        """
        Возвращает копию текущего хранилища настроек.
        """
        return dict(self._settings)

    def get_setting(self, key: str) -> object:
        """
        Возвращает значение настройки по ключу.
        Если ключ отсутствует - возвращается default_value.
        :param key: Ключ настройки (непустая строка)
        """
        self._check_key(key)
        return self._settings.get(key, self._default_value)

    def set_setting(self, key: str, value: object) -> None:
        """
        Устанавливает значение настройки по ключу.
        :param key: Ключ настройки (непустая строка)
        :param value: Любое значение настройки
        """
        self._check_key(key)
        self._settings[key] = value

    def has_setting(self, key: str) -> bool:
        """
        Проверяет наличие настройки в хранилище.
        :param key: Ключ настройки
        """
        self._check_key(key)
        return key in self._settings

    @staticmethod
    def _check_key(key: str) -> None:
        """
        Проверяет корректность ключа настройки.
        :param key: Проверяемый ключ
        """
        if not isinstance(key, str) or not key.strip():
            raise arguments_exception('Ключ настройки должен быть непустой строкой', 'key')

    def convert(self, obj: object = None, schema: Optional[dict[str, tuple]] = None) -> dict:
        """
        Формирует результат конвертации настроек по схеме.

        Метод только ФОРМИРУЕТ данные (словарь '<имя поля>': <значение>);
        загрузка/построение объектов сторонними механизмами не выполняется.

        :param obj: Источник настроек. Допускается:
                    None (используется внутреннее хранилище),
                    dict (конвертируется переданный словарь).
        :param schema: Схема конвертации
                       { '<имя поля>': ('<ключ настройки>', <тип>) }.
                       Тип может быть None - значение возвращается как есть.
                       Схема необязательна: без нее возвращается копия словаря.
        :return: Словарь сформированных полей (или копия словаря настроек,
                 если схема не задана).
        """
        if obj is None:
            source = dict(self._settings)
        elif isinstance(obj, dict):
            source = obj
        else:
            raise arguments_exception(
                'Для конвертации передан некорректный источник настроек', 'obj')

        if schema is None:
            return source

        if not isinstance(schema, dict):
            raise arguments_exception('Схема конвертации должна быть словарем', 'schema')

        result: dict[str, object] = {}
        for field, spec in schema.items():
            if (not isinstance(spec, tuple) or len(spec) != 2
                    or not isinstance(spec[0], str)):
                raise arguments_exception(
                    f'Некорректная схема конвертации для поля "{field}"', 'schema')
            key, target_type = spec
            value = source.get(key, self._default_value)
            if target_type is not None and value is not None:
                try:
                    value = target_type(value)
                except (TypeError, ValueError):
                    raise arguments_exception(
                        f'Невозможно привести значение настройки "{key}" к типу '
                        f'{target_type.__name__}', field)
            result[field] = value
        return result
