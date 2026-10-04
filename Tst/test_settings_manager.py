import pytest

from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception
from Src.Core.settings_manager import settings_manager


# ----------------------------------------------------------------------
# Проверка наследования и общего поведения менеджера
# ----------------------------------------------------------------------


def test_is_inherited_from_abstract_manager_success():
    """
    settings_manager является наследником abstract_manager и корректно создается.
    """
    # Действие
    manager = settings_manager()

    # Проверка
    assert isinstance(manager, abstract_manager)


def test_raise_type_error_when_instantiate_abstract_manager():
    """
    Абстрактный класс abstract_manager нельзя инстанцировать напрямую:
    у него не реализован абстрактный метод convert.
    """
    # Действие и проверка
    with pytest.raises(TypeError):
        abstract_manager()


def test_get_empty_settings_returns_default_value_success():
    """
    В пустом хранилище get_setting возвращает default_value для любого ключа.
    """
    # Подготовка
    manager = settings_manager(default_value='нет значения')

    # Действие
    result = manager.get_setting('language')

    # Проверка
    assert result == 'нет значения'


# ----------------------------------------------------------------------
# Операции set/get/has со настройками
# ----------------------------------------------------------------------


def test_set_and_get_setting_returns_same_value_success():
    """
    Установленная настройка возвращается методом get_setting без изменений.
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.set_setting('language', 'ru')

    # Проверка
    assert manager.get_setting('language') == 'ru'
    assert manager.has_setting('language') is True


def test_init_with_settings_dict_loads_all_values_success():
    """
    Конструктор с начальным словарем настроек загружает все пары ключ-значение.
    """
    # Подготовка
    initial = {'language': 'ru', 'currency': 'RUB', 'delivery_fee': 150}

    # Действие
    manager = settings_manager(initial)

    # Проверка
    assert manager.settings == initial
    assert manager.get_setting('currency') == 'RUB'


def test_settings_property_returns_copy_not_internal_storage_success():
    """
    Свойство settings возвращает копию: изменение копии не влияет на хранилище.
    """
    # Подготовка
    manager = settings_manager({'a': 1})

    # Действие
    copy = manager.settings
    copy['a'] = 999
    copy['b'] = 2

    # Проверка
    assert manager.get_setting('a') == 1
    assert manager.has_setting('b') is False


def test_overwrite_existing_setting_success():
    """
    Повторная установка значения по существующему ключу перезаписывает его.
    """
    # Подготовка
    manager = settings_manager({'region': 'Москва'})

    # Действие
    manager.set_setting('region', 'Санкт-Петербург')

    # Проверка
    assert manager.get_setting('region') == 'Санкт-Петербург'


def test_has_setting_false_for_unknown_key_success():
    """
    Для отсутствующего ключа has_setting возвращает False.
    """
    # Подготовка
    manager = settings_manager()

    # Проверка
    assert manager.has_setting('unknown') is False


@pytest.mark.parametrize('bad_key', ['', '   ', None, 123])
def test_raise_arguments_exception_when_key_invalid(bad_key):
    """
    Пустой, состоящий из пробелов или нестроковый ключ настройки вызывает arguments_exception.
    """
    # Подготовка
    manager = settings_manager()

    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.set_setting(bad_key, 'value')


# ----------------------------------------------------------------------
# Метод convert
# ----------------------------------------------------------------------


def test_convert_without_schema_returns_settings_copy_success():
    """
    Без схемы convert возвращает копию внутреннего хранилища настроек.
    """
    # Подготовка
    manager = settings_manager({'language': 'ru', 'week_start': 'monday'})

    # Действие
    result = manager.convert()

    # Проверка
    assert result == {'language': 'ru', 'week_start': 'monday'}
    result['language'] = 'de'
    assert manager.get_setting('language') == 'ru'


def test_convert_uses_explicit_dict_source_success():
    """
    Convert конвертирует явно переданный словарь, не затрагивая хранилище.
    """
    # Подготовка
    manager = settings_manager()
    source = {'name': 'Ромашка', 'inn': '1234567890'}

    # Действие
    result = manager.convert(source, schema={'title': ('name', str),
                                             'code': ('inn', str)})

    # Проверка
    assert result['title'] == 'Ромашка'
    assert result['code'] == '1234567890'


def test_convert_by_schema_casts_types_success():
    """
    Convert приводит значения настроек к типам из схемы (str -> int).
    """
    # Подготовка
    manager = settings_manager({'fee': '150', 'enabled': 'true'})

    # Действие
    result = manager.convert(schema={'delivery_fee': ('fee', int),
                                     'is_enabled': ('enabled', None)})

    # Проверка
    assert result['delivery_fee'] == 150
    assert isinstance(result['delivery_fee'], int)
    assert result['is_enabled'] == 'true'


def test_convert_missing_key_filled_with_default_value_success():
    """
    Для отсутствующего в источнике ключа подставляется default_value.
    """
    # Подготовка
    manager = settings_manager({'only_key': 1}, default_value=0)

    # Действие
    result = manager.convert(schema={'known': ('only_key', int),
                                     'missing': ('absent_key', int)})

    # Проверка
    assert result['known'] == 1
    assert result['missing'] == 0


def test_convert_none_value_kept_without_cast_success():
    """
    Значение None не приводится к типу схемы и остается None.
    """
    # Подготовка
    manager = settings_manager({'empty': None})

    # Действие
    result = manager.convert(schema={'field': ('empty', int)})

    # Проверка
    assert result['field'] is None


def test_raise_arguments_exception_when_convert_bad_source():
    """
    Некорректный источник конвертации (не dict и не None) вызывает arguments_exception.
    """
    # Подготовка
    manager = settings_manager()

    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.convert([1, 2, 3])


def test_raise_arguments_exception_when_convert_bad_schema_spec():
    """
    Некорректная схема (спецификация поля не кортеж из двух элементов)
    вызывает arguments_exception.
    """
    # Подготовка
    manager = settings_manager({'a': 1})

    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.convert(schema={'field': 'just_string'})


def test_raise_arguments_exception_when_convert_bad_schema_type():
    """
    Схема конвертации обязана быть словарем, иначе arguments_exception.
    """
    # Подготовка
    manager = settings_manager()

    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.convert({'a': 1}, schema=['not', 'a', 'dict'])


def test_raise_arguments_exception_when_convert_impossible_cast():
    """
    Невозможность приведения значения к типу схемы вызывает arguments_exception.
    """
    # Подготовка
    manager = settings_manager({'fee': 'abc'})

    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.convert(schema={'delivery_fee': ('fee', int)})
