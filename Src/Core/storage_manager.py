import threading
from typing import Any, Optional, TypeVar

from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception
from Src.Core.abstract_model import abstract_model
from Src.Models.storage_model import storage_model
from Src.Models.unit_model import unit_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model

# Тип доменной модели, обрабатываемый generic-операциями хранилища.
_T = TypeVar('_T', storage_model, unit_model, nomenclature_model,
              nomenclature_group_model)


class storage_manager(abstract_manager):
    """
    Менеджер-хранилище данных по доменным моделям (паттерн Singleton).

    Хранит в памяти уникальные объекты доменных сущностей четырех видов:
        - склады (storage_model);
        - единицы измерения (unit_model);
        - номенклатура (nomenclature_model);
        - группы номенклатуры (nomenclature_group_model).

    Гарантии:
        - Класс является синглтоном: все обращения к конструктору возвращают
          один и тот же экземпляр (с потокобезопасной инициализацией).
        - Каждый элемент уникален: повторное добавление объекта с тем же id
          считается ошибкой дубликата.

    Правила первого старта:
        - При первой инициализации экземпляра (первый старт приложения)
          автоматически формируются первичные данные: базовые единицы
          измерения, склады, группы номенклатуры и позиции номенклатуры.
        - Метод initialize() идемпотентен: повторные вызовы не создают
          данные заново.
    """

    # Признак того, что первичные данные уже сформированы (первый старт выполнен).
    _initialized: bool = False

    # Блокировка для потокобезопасной работы с коллекциями.
    _lock: threading.RLock

    # Хранилища по видам доменных сущностей: id сущности -> объект.
    _storages: dict[str, storage_model]
    _units: dict[str, unit_model]
    _nomenclatures: dict[str, nomenclature_model]
    _groups: dict[str, nomenclature_group_model]

    # Экземпляр синглтона (None до первого создания).
    __instance: Optional['storage_manager'] = None

    # Защита от повторного выполнения __init__ у уже созданного синглтона.
    __singleton_lock: threading.Lock = threading.Lock()
    __created: bool = False

    def __new__(cls, *args, **kwargs) -> 'storage_manager':
        """
        Создает экземпляр один раз (Singleton); далее возвращает сохраненный экземпляр.
        Инициализация потокобезопасна (двойная проверка под блокировкой).
        """
        if cls.__instance is None:
            with cls.__singleton_lock:
                if cls.__instance is None:
                    instance = super().__new__(cls)
                    cls.__instance = instance
        return cls.__instance

    def __init__(self) -> None:
        """
        Инициализация хранилища. Повторные вызовы (при обращении к синглтону)
        не переинициализируют состояние.
        """
        if storage_manager.__created:
            return
        with storage_manager.__singleton_lock:
            if storage_manager.__created:
                return
            self._lock = threading.RLock()
            self._storages = {}
            self._units = {}
            self._nomenclatures = {}
            self._groups = {}
            storage_manager.__created = True
        # Первый старт: формируем первичные данные.
        self.initialize()

    # ------------------------------------------------------------------
    # Шаблонный метод convert (реализация абстрактного метода родителя)
    # ------------------------------------------------------------------

    def convert(self, obj: Any) -> Any:
        """
        Преобразует объект в канонический вид хранилища.

        Варианты преобразования:
            - Доменная модель (abstract_model) -> копия словаря ее атрибутов
              (для сериализации/выгрузки).
            - Словарь с ключом 'type' ('storage' | 'unit' | 'nomenclature' |
              'group') -> соответствующая доменная модель (для загрузки данных).

        :param obj: Исходный объект (доменная модель либо словарь)
        :return: Словарь атрибутов модели либо экземпляр доменной модели
        """
        if isinstance(obj, abstract_model):
            return self.__to_dict(obj)

        if isinstance(obj, dict):
            entity_type = obj.get('type')
            # Допускается канонический вид имени модели: 'unit_model' -> 'unit'.
            if isinstance(entity_type, str) and entity_type.endswith('_model'):
                entity_type = entity_type[:-len('_model')]
            name = obj.get('name')
            if not isinstance(name, str) or not name.strip():
                raise arguments_exception('В словаре отсутствует корректное наименование', 'name')
            if entity_type == 'storage':
                return storage_model(name=name, address=obj.get('address'),
                                     id=obj.get('id'))
            if entity_type == 'unit':
                base_unit = obj.get('base_unit')
                if base_unit is not None and not isinstance(base_unit, unit_model):
                    raise arguments_exception(
                        'Базовая единица должна быть экземпляром unit_model', 'base_unit')
                return unit_model(name=name, coefficient=obj.get('coefficient', 1),
                                  base_unit=base_unit, id=obj.get('id'))
            if entity_type == 'group':
                units = obj.get('units')
                if not isinstance(units, (list, tuple)):
                    raise arguments_exception(
                        'Единицы измерения группы должны быть списком', 'units')
                for unit in units:
                    if not isinstance(unit, unit_model):
                        raise arguments_exception(
                            'В состав группы можно включать только unit_model', 'units')
                return nomenclature_group_model(name=name, units=list(units),
                                                id=obj.get('id'))
            if entity_type == 'nomenclature':
                group = obj.get('group')
                unit = obj.get('unit')
                if not isinstance(group, nomenclature_group_model):
                    raise arguments_exception(
                        'Группа номенклатуры должна быть экземпляром nomenclature_group_model',
                        'group')
                if not isinstance(unit, unit_model):
                    raise arguments_exception(
                        'Единица измерения должна быть экземпляром unit_model', 'unit')
                return nomenclature_model(name=name, full_name=obj.get('full_name'),
                                          group=group, unit=unit,
                                          id=obj.get('id'))
            raise arguments_exception(
                f'Неизвестный тип объекта для конвертации: {entity_type}', 'type')

        raise arguments_exception(
            'Конвертируемый объект должен быть доменной моделью или словарем', 'obj')

    @staticmethod
    def __to_dict(model: abstract_model) -> dict:
        """
        Возвращает словарь публичных атрибутов доменной модели.
        :param model: Преобразуемая доменная модель
        """
        result: dict[str, Any] = {'type': type(model).__name__,
                                  'id': model.id, 'name': model.name}
        for key, value in vars(model).items():
            if key.startswith('_'):
                result[key.lstrip('_')] = value
        return result

    # ------------------------------------------------------------------
    # Первый старт: формирование первичных данных
    # ------------------------------------------------------------------

    @property
    def initialized(self) -> bool:
        """
        Признак выполнения первого старта (первичные данные сформированы).
        """
        return self._initialized

    def initialize(self) -> None:
        """
        Формирует первичные данные при первом старте приложения.
        Метод идемпотентен: повторный вызов ничего не делает.
        """
        with self._lock:
            if self._initialized:
                return
            self.__create_initial_data()
            self._initialized = True

    def __create_initial_data(self) -> None:
        """
        Создает набор первичных данных: единицы измерения, склады,
        группы номенклатуры и позиции номенклатуры.
        """
        # Единицы измерения: базовые и производные.
        gram = self.add_unit(unit_model('грамм', 1))
        kilogram = self.add_unit(unit_model('кг', 1000, gram))
        milliliter = self.add_unit(unit_model('мл', 1))
        liter = self.add_unit(unit_model('л', 1000, milliliter))
        piece = self.add_unit(unit_model('шт', 1))
        dozen = self.add_unit(unit_model('дюжина', 12, piece))

        # Склады сети ресторанов.
        self.add_storage(storage_model('Центральный склад'))
        self.add_storage(storage_model('Склад производственного цеха'))
        for number in range(1, 11):
            self.add_storage(storage_model(f'Склад ресторана №{number}'))

        # Группы номенклатуры.
        dairy_group = self.add_group(
            nomenclature_group_model('Молочные продукты', [kilogram, liter, piece]))
        meat_group = self.add_group(
            nomenclature_group_model('Мясные продукты', [kilogram, gram]))
        grocery_group = self.add_group(
            nomenclature_group_model('Бакалея', [kilogram, gram, piece]))
        beverage_group = self.add_group(
            nomenclature_group_model('Напитки', [liter, milliliter, dozen]))

        # Позиции номенклатуры.
        self.add_nomenclature(nomenclature_model('Молоко', 'Молоко коровье пастеризованное 3,2%',
                                                 dairy_group, liter))
        self.add_nomenclature(nomenclature_model('Сметана', 'Сметана 20% фасованная',
                                                 dairy_group, kilogram))
        self.add_nomenclature(nomenclature_model('Говядина', 'Говядина охлажденная 1 сорт',
                                                 meat_group, kilogram))
        self.add_nomenclature(nomenclature_model('Курица', 'Филе куриное охлажденное',
                                                 meat_group, kilogram))
        self.add_nomenclature(nomenclature_model('Мука', 'Мука пшеничная высший сорт',
                                                 grocery_group, kilogram))
        self.add_nomenclature(nomenclature_model('Сахар', 'Сахар-песок',
                                                 grocery_group, kilogram))
        self.add_nomenclature(nomenclature_model('Соль', 'Соль пищевая мелкая',
                                                 grocery_group, gram))
        self.add_nomenclature(nomenclature_model('Вода', 'Вода питьевая бутилированная',
                                                 beverage_group, liter))

    # ------------------------------------------------------------------
    # Операции со складами
    # ------------------------------------------------------------------

    def add_storage(self, obj: storage_model) -> storage_model:
        """
        Добавляет склад в хранилище. Объект обязан быть уникальным по id.
        :param obj: Экземпляр storage_model
        """
        return self._add_item(self._storages, obj, storage_model, 'storage')

    def get_storage(self, id: str) -> Optional[storage_model]:
        """
        Возвращает склад по идентификатору либо None.
        """
        return self._get_item(self._storages, id)

    def remove_storage(self, id: str) -> None:
        """
        Удаляет склад из хранилища по идентификатору.
        """
        self._remove_item(self._storages, id)

    @property
    def storages(self) -> list[storage_model]:
        """
        Возвращает список всех складов хранилища.
        """
        return self._get_all(self._storages)

    # ------------------------------------------------------------------
    # Операции с единицами измерения
    # ------------------------------------------------------------------

    def add_unit(self, obj: unit_model) -> unit_model:
        """
        Добавляет единицу измерения в хранилище. Объект обязан быть уникальным по id.
        :param obj: Экземпляр unit_model
        """
        return self._add_item(self._units, obj, unit_model, 'unit')

    def get_unit(self, id: str) -> Optional[unit_model]:
        """
        Возвращает единицу измерения по идентификатору либо None.
        """
        return self._get_item(self._units, id)

    def remove_unit(self, id: str) -> None:
        """
        Удаляет единицу измерения из хранилища по идентификатору.
        """
        self._remove_item(self._units, id)

    @property
    def units(self) -> list[unit_model]:
        """
        Возвращает список всех единиц измерения хранилища.
        """
        return self._get_all(self._units)

    # ------------------------------------------------------------------
    # Операции с номенклатурой
    # ------------------------------------------------------------------

    def add_nomenclature(self, obj: nomenclature_model) -> nomenclature_model:
        """
        Добавляет позицию номенклатуры в хранилище. Объект обязан быть уникальным по id.
        :param obj: Экземпляр nomenclature_model
        """
        return self._add_item(self._nomenclatures, obj, nomenclature_model, 'nomenclature')

    def get_nomenclature(self, id: str) -> Optional[nomenclature_model]:
        """
        Возвращает позицию номенклатуры по идентификатору либо None.
        """
        return self._get_item(self._nomenclatures, id)

    def remove_nomenclature(self, id: str) -> None:
        """
        Удаляет позицию номенклатуры из хранилища по идентификатору.
        """
        self._remove_item(self._nomenclatures, id)

    @property
    def nomenclatures(self) -> list[nomenclature_model]:
        """
        Возвращает список всех позиций номенклатуры хранилища.
        """
        return self._get_all(self._nomenclatures)

    # ------------------------------------------------------------------
    # Операции с группами номенклатуры
    # ------------------------------------------------------------------

    def add_group(self, obj: nomenclature_group_model) -> nomenclature_group_model:
        """
        Добавляет группу номенклатуры в хранилище. Объект обязан быть уникальным по id.
        :param obj: Экземпляр nomenclature_group_model
        """
        return self._add_item(self._groups, obj, nomenclature_group_model, 'group')

    def get_group(self, id: str) -> Optional[nomenclature_group_model]:
        """
        Возвращает группу номенклатуры по идентификатору либо None.
        """
        return self._get_item(self._groups, id)

    def remove_group(self, id: str) -> None:
        """
        Удаляет группу номенклатуры из хранилища по идентификатору.
        """
        self._remove_item(self._groups, id)

    @property
    def groups(self) -> list[nomenclature_group_model]:
        """
        Возвращает список всех групп номенклатуры хранилища.
        """
        return self._get_all(self._groups)

    # ------------------------------------------------------------------
    # Служебные операции
    # ------------------------------------------------------------------

    def find_by_name(self, collection_name: str, name: str) -> list[abstract_model]:
        """
        Возвращает список объектов указанного хранилища с заданным наименованием.
        :param collection_name: Имя хранилища: 'storages' | 'units' |
                                'nomenclatures' | 'groups'
        :param name: Искомое наименование (без учета регистра)
        """
        collections = {
            'storages': self._storages,
            'units': self._units,
            'nomenclatures': self._nomenclatures,
            'groups': self._groups,
        }
        if collection_name not in collections:
            raise arguments_exception('Неизвестное хранилище для поиска', 'collection_name')
        if not isinstance(name, str) or not name.strip():
            raise arguments_exception('Наименование должно быть непустой строкой', 'name')
        needle = name.strip().lower()
        with self._lock:
            return [item for item in collections[collection_name].values()
                    if item.name is not None and item.name.lower() == needle]

    def clear(self) -> None:
        """
        Полностью очищает все хранилища и сбрасывает признак первого старта.
        Предназначен для тестирования и повторной инициализации.
        """
        with self._lock:
            self._storages.clear()
            self._units.clear()
            self._nomenclatures.clear()
            self._groups.clear()
            self._initialized = False

    @classmethod
    def reset_instance(cls) -> None:
        """
        Сбрасывает экземпляр синглтона. Используется только в тестах.
        """
        with cls.__singleton_lock:
            cls.__instance = None
            cls.__created = False

    # ------------------------------------------------------------------
    # Внутренняя реализация generic-операций
    # ------------------------------------------------------------------

    def _add_item(self, container: dict[str, _T], obj: _T,
                  expected_type: type[_T], kind: str) -> _T:
        """
        Проверяет тип и уникальность объекта и помещает его в контейнер.
        :param container: Целевое хранилище (словарь id -> объект)
        :param obj: Добавляемый доменный объект
        :param expected_type: Ожидаемый тип доменной модели
        :param kind: Наименование вида сущности для сообщения об ошибке
        """
        if not isinstance(obj, expected_type):
            raise arguments_exception(
                f'В хранилище "{kind}" можно добавлять только {expected_type.__name__}', 'obj')
        with self._lock:
            if obj.id in container:
                raise arguments_exception(
                    f'Объект с таким идентификатором уже присутствует в хранилище "{kind}"', 'obj')
            container[obj.id] = obj
        return obj

    def _get_item(self, container: dict[str, _T], id: str) -> Optional[_T]:
        """
        Возвращает объект из контейнера по идентификатору либо None.
        """
        if not isinstance(id, str) or not id.strip():
            raise arguments_exception('Идентификатор должен быть непустой строкой', 'id')
        with self._lock:
            return container.get(id.strip())

    def _remove_item(self, container: dict[str, _T], id: str) -> None:
        """
        Удаляет объект из контейнера по идентификатору.
        Отсутствие объекта не считается ошибкой.
        """
        if not isinstance(id, str) or not id.strip():
            raise arguments_exception('Идентификатор должен быть непустой строкой', 'id')
        with self._lock:
            container.pop(id.strip(), None)

    def _get_all(self, container: dict[str, _T]) -> list[_T]:
        """
        Возвращает список всех объектов контейнера (копию).
        """
        with self._lock:
            return list(container.values())
