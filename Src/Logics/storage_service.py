from collections import Counter
from typing import Dict, List, Tuple
from Src.Core.validator import (
    validator,
    operation_exception,
    argument_exception,
    not_found_exception,
    conflict_exception,
)
from Src.Logics.storage_manager import storage_manager
from Src.Logics.mapping_factory import mapping_factory
from Src.Logics.convertor import convertor
from Src.Logics.prototype import prototype
from Src.Logics.osv_service import osv_service
from Src.Dtos.filter_dto import filter_dto


class storage_service:
    """Сервис бизнес-логики для CRUD-операций и поддержания обратного индекса связей."""

    # Хранилище доменных данных
    __storage: storage_manager = None
    # Фабрика сопоставлений DTO и моделей
    __mapping_factory: mapping_factory = None
    # Конвертор
    __convertor: convertor = None

    # Прямые зависимости: owner_code -> Counter(target_code: count)
    __outgoing: Dict[str, Counter] = None
    # Обратный индекс связей: target_code -> {owner_code: count}
    __incoming: Dict[str, Dict[str, int]] = None

    # Singletone
    def __new__(cls, storage: storage_manager = None):
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_service, cls).__new__(cls)
        return cls.instance

    def __init__(self, storage: storage_manager = None):
        """Инициализировать сервис хранилища с инъекцией менеджера данных."""
        if storage is not None:
            self.__storage = storage
        elif self.__storage is None and hasattr(storage_manager, "instance"):
            self.__storage = storage_manager.instance

        self.__mapping_factory = mapping_factory()
        self.__convertor = convertor()
        self.__outgoing = {}
        self.__incoming = {}
        if self.__storage is not None:
            self.build_index()

    @property
    def storage(self) -> storage_manager:
        """Получить экземпляр менеджера хранилища."""
        return self.__storage

    @storage.setter
    def storage(self, value: storage_manager) -> None:
        """Установить экземпляр менеджера хранилища и перестроить индекс."""
        self.__storage = value
        self.build_index()

    @property
    def incoming_index(self) -> Dict[str, Dict[str, int]]:
        """Текущее состояние обратного индекса связей."""
        return self.__incoming

    @property
    def outgoing_index(self) -> Dict[str, Counter]:
        """Текущее состояние прямых исходящих связей."""
        return self.__outgoing

    def build_index(self) -> None:
        """Построить обратный индекс связей по текущим данным хранилища."""
        self.__outgoing.clear()
        self.__incoming.clear()

        if self.__storage is None or not hasattr(self.__storage, "data"):
            return

        for entity_key, items in self.__storage.data.items():
            for item in items:
                code = getattr(item, "unique_code", None)
                if code:
                    refs = item.get_references() if hasattr(item, "get_references") else []
                    self._add_outgoing_refs(code, refs)

    def _add_outgoing_refs(self, owner_code: str, refs: list) -> None:
        """Добавить исходящие связи объекта в прямой и обратный индексы."""
        owner_code = str(owner_code).strip()
        target_codes = [
            getattr(r, "unique_code", "").strip()
            for r in refs
            if r is not None and getattr(r, "unique_code", "").strip() != ""
        ]
        target_counter = Counter(target_codes)
        self.__outgoing[owner_code] = target_counter

        for target_code, cnt in target_counter.items():
            if target_code not in self.__incoming:
                self.__incoming[target_code] = {}
            self.__incoming[target_code][owner_code] = (
                self.__incoming[target_code].get(owner_code, 0) + cnt
            )

    def _remove_outgoing_refs(self, owner_code: str) -> None:
        """Удалить исходящие связи объекта из прямого и обратного индексов."""
        owner_code = str(owner_code).strip()
        if owner_code in self.__outgoing:
            target_counter = self.__outgoing.pop(owner_code)
            for target_code, cnt in target_counter.items():
                if target_code in self.__incoming:
                    if owner_code in self.__incoming[target_code]:
                        self.__incoming[target_code][owner_code] -= cnt
                        if self.__incoming[target_code][owner_code] <= 0:
                            del self.__incoming[target_code][owner_code]
                    if len(self.__incoming[target_code]) == 0:
                        del self.__incoming[target_code]

    def _update_outgoing_refs(self, old_owner_code: str, new_owner_code: str, new_refs: list) -> None:
        """Обновить исходящие связи объекта при его модификации."""
        self._remove_outgoing_refs(old_owner_code)
        self._add_outgoing_refs(new_owner_code, new_refs)

    def is_linked(self, unique_code: str) -> Tuple[bool, str]:
        """Быстрая проверка наличия входящих ссылок на сущность по обратному индексу."""
        validator.validate(unique_code, str)
        code = unique_code.strip()
        if code in self.__incoming and len(self.__incoming[code]) > 0:
            owners = list(self.__incoming[code].keys())
            owner_names = []
            for o_code in owners:
                obj = self._find_object_by_code(o_code)
                name = getattr(obj, "name", o_code) if obj else o_code
                owner_names.append(f"'{name}' (код: {o_code})")
            return True, f"на сущность ссылаются: {', '.join(owner_names)}"
        return False, ""

    def get_incoming_references(self, unique_code: str) -> Dict[str, int]:
        """Получить словарь владельцев, ссылающихся на уникальный код."""
        validator.validate(unique_code, str)
        return dict(self.__incoming.get(unique_code.strip(), {}))

    def _find_object_by_code(self, unique_code: str):
        """Найти объект с указанным кодом по всем коллекциям хранилища."""
        code = unique_code.strip()
        if self.__storage is None or not hasattr(self.__storage, "data"):
            return None
        for collection in self.__storage.data.values():
            for item in collection:
                if getattr(item, "unique_code", None) == code:
                    return item
                if hasattr(item, "items"):
                    for sub in item.items:
                        if getattr(sub, "unique_code", None) == code:
                            return sub
                if hasattr(item, "ingredients"):
                    for sub in item.ingredients:
                        if getattr(sub, "unique_code", None) == code:
                            return sub
        return None

    def is_code_unique(self, unique_code: str, ignore_code: str = "") -> bool:
        """Проверить, что уникальный код не занят в хранилище."""
        code = unique_code.strip()
        if not code:
            return True
        if self.__storage is None or not hasattr(self.__storage, "data"):
            return True
        ignore = ignore_code.strip()
        for collection in self.__storage.data.values():
            for item in collection:
                item_code = getattr(item, "unique_code", None)
                if item_code and item_code == code and item_code != ignore:
                    return False
        return True

    def deserialize_item(self, entity_type: str, data: dict):
        """Десериализовать словарь в доменную модель через общий механизм десериализации."""
        validator.validate(entity_type, str)
        validator.validate(data, dict)

        payload = dict(data)
        if "type" not in payload:
            dto_name = self.__mapping_factory.get_dto_type_name(entity_type)
            if not dto_name:
                raise not_found_exception(f"Тип сущности '{entity_type}' не поддерживается")
            payload["type"] = dto_name

        self.__convertor = convertor()
        item = self.__convertor.deserialize(payload)
        if self.__convertor.is_error or item is None:
            err = self.__convertor.error_text or "Ошибка десериализации данных"
            raise operation_exception(err)

        expected_domain = self.__mapping_factory.get_domain_type(entity_type)
        if expected_domain and not isinstance(item, expected_domain):
            raise operation_exception(
                f"Десериализованный объект типа {type(item).__name__} не соответствует {expected_domain.__name__}"
            )

        return item

    def get_all(self, entity_type: str) -> list:
        """Получить список всех объектов сущности указанного типа."""
        validator.validate(entity_type, str)
        if entity_type not in self.__storage.data:
            raise not_found_exception(f"Тип сущности '{entity_type}' не поддерживается")
        return list(self.__storage.data[entity_type])

    def get_by_code(self, entity_type: str, unique_code: str) -> object:
        """Получить объект сущности по ключу коллекции и уникальному коду."""
        validator.validate(entity_type, str)
        validator.validate(unique_code, str)
        if entity_type not in self.__storage.data:
            raise not_found_exception(f"Тип сущности '{entity_type}' не поддерживается")

        item = self.__storage.get_item(entity_type, unique_code)
        if item is None:
            raise not_found_exception(f"Сущность с кодом '{unique_code}' не найдена")
        return item

    def create(self, entity_type: str, data: dict) -> object:
        """Создать новую доменную сущность с предварительной валидацией и регистрацией связей."""
        validator.validate(entity_type, str)
        if not isinstance(data, dict):
            raise argument_exception("Тело запроса должно быть JSON-объектом!")

        if entity_type not in self.__storage.data:
            raise not_found_exception(f"Тип сущности '{entity_type}' не поддерживается")

        # Проверка уникальности кода до десериализации
        code = data.get("unique_code")
        if code:
            code_str = str(code).strip()
            if not self.is_code_unique(code_str):
                raise conflict_exception(f"Сущность с кодом '{code_str}' уже существует!")

        # Десериализация и создание кандидата
        candidate = self.deserialize_item(entity_type, data)
        cand_code = candidate.unique_code
        if not self.is_code_unique(cand_code):
            raise conflict_exception(f"Сущность с кодом '{cand_code}' уже существует!")

        # Добавление в хранилище
        self.__storage.add_item(entity_type, candidate)

        # Регистрация связей нового объекта в индексе
        refs = candidate.get_references() if hasattr(candidate, "get_references") else []
        self._add_outgoing_refs(cand_code, refs)

        return candidate

    def update(self, entity_type: str, unique_code: str, data: dict) -> object:
        """Обновить существующую сущность с сохранением ссылочной целостности и ссылок в памяти."""
        validator.validate(entity_type, str)
        validator.validate(unique_code, str)
        if not isinstance(data, dict):
            raise argument_exception("Тело запроса должно быть JSON-объектом!")

        if entity_type not in self.__storage.data:
            raise not_found_exception(f"Тип сущности '{entity_type}' не поддерживается")

        existing = self.__storage.get_item(entity_type, unique_code)
        if existing is None:
            raise not_found_exception(f"Сущность с кодом '{unique_code}' не найдена")

        payload = dict(data)
        raw_code = payload.get("unique_code")
        if not raw_code or str(raw_code).strip() == "":
            new_code_str = unique_code
            payload["unique_code"] = unique_code
        else:
            new_code_str = str(raw_code).strip()

        # Если меняется уникальный код
        if new_code_str != unique_code:
            linked, reason = self.is_linked(unique_code)
            if linked:
                raise conflict_exception(f"Запрещено изменять код сущности: {reason}")
            if not self.is_code_unique(new_code_str, ignore_code=unique_code):
                raise conflict_exception(f"Сущность с кодом '{new_code_str}' уже существует!")

        # Создаем и полностью валидируем кандидата
        candidate = self.deserialize_item(entity_type, payload)
        candidate.unique_code = new_code_str

        if type(candidate) is not type(existing):
            raise operation_exception(
                f"Несоответствие типов: ожидается {type(existing).__name__}, получен {type(candidate).__name__}"
            )

        # Обновляем индекс связей
        new_refs = candidate.get_references() if hasattr(candidate, "get_references") else []
        self._update_outgoing_refs(unique_code, new_code_str, new_refs)

        # Применяем состояние к существующему экземпляру в памяти
        try:
            existing.update_from(candidate)
        except Exception as ex:
            # Откат связей при сбое применения
            old_refs = existing.get_references() if hasattr(existing, "get_references") else []
            self._update_outgoing_refs(new_code_str, unique_code, old_refs)
            raise ex

        return existing

    def delete(self, entity_type: str, unique_code: str) -> bool:
        """Удалить сущность с проверкой запрета на удаление используемых объектов."""
        validator.validate(entity_type, str)
        validator.validate(unique_code, str)

        if entity_type not in self.__storage.data:
            raise not_found_exception(f"Тип сущности '{entity_type}' не поддерживается")

        existing = self.__storage.get_item(entity_type, unique_code)
        if existing is None:
            raise not_found_exception(f"Сущность с кодом '{unique_code}' не найдена")

        linked, reason = self.is_linked(unique_code)
        if linked:
            raise conflict_exception(f"Запрещено удалять сущность: {reason}")

        # Удаляем исходящие связи удаляемой сущности
        self._remove_outgoing_refs(unique_code)

        # Удаляем объект из хранилища
        self.__storage.delete_item(entity_type, unique_code)

        return True

    def resolve_entity_type(self, entity_type: str) -> str:
        """Нормализовать ключ коллекции сущностей по короткому имени или имени модели."""
        validator.validate(entity_type, str)
        key = entity_type.strip()
        if self.__storage is not None and hasattr(self.__storage, "data"):
            if key in self.__storage.data:
                return key
            if f"{key}_model" in self.__storage.data:
                return f"{key}_model"
            if key in ("recipe", "recipe_model"):
                return storage_manager.receipt_key()
            for k in self.__storage.data.keys():
                if k.lower() == key.lower() or k.lower() == f"{key.lower()}_model":
                    return k
        raise not_found_exception(f"Тип сущности '{entity_type}' не поддерживается")

    def filter_entities(self, entity_type: str, filter_data: dict) -> list:
        """Отфильтровать доменные сущности указанного типа через шаблон Прототип."""
        canonical_key = self.resolve_entity_type(entity_type)
        if not isinstance(filter_data, dict):
            raise argument_exception("Тело запроса фильтрации должно быть JSON-объектом!")

        dto = filter_dto().from_dict(filter_data)
        items = list(self.__storage.data[canonical_key])
        return prototype(items).clone(dto).data

    def build_osv(self, filter_data: dict = None) -> list:
        """Сформировать оборотно-сальдовую ведомость через сервис ОСВ."""
        return osv_service(self.__storage).build(filter_data)
