# UML-диаграммы менеджеров: `settings_manager` и `storage_manager`

> Диаграммы выполнены в формате Mermaid (markdown).
> Ветки: `feat/caching`, код: `Src/Core/abstract_manager.py`, `Src/Core/settings_manager.py`, `Src/Core/storage_manager.py`.

---

## 1. Диаграмма классов (Class Diagram)

Общая структура: оба менеджера наследуют абстрактный класс `abstract_manager`
и переопределяют шаблонный метод `convert`. `storage_manager` реализован
как потокобезопасный **Singleton** и оперирует доменными моделями,
наследующими `abstract_model`.

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        +convert(obj: Any) Any*
    }

    class settings_manager {
        -_settings : dict~str, Any~
        -_default_value : Any
        +default_value : Any <<property>>
        +settings : dict~str, Any~ <<property>>
        +get_setting(key: str) Any
        +set_setting(key: str, value: Any) None
        +has_setting(key: str) bool
        +convert(obj: Any = None, schema: dict = None) SimpleNamespace
        -_check_key(key: str) None «static»
    }

    class storage_manager {
        <<Singleton>>
        -__instance : storage_manager$
        -__created : bool$
        -__singleton_lock : Lock$
        -_initialized : bool
        -_lock : RLock
        -_storages : dict~str, storage_model~
        -_units : dict~str, unit_model~
        -_nomenclatures : dict~str, nomenclature_model~
        -_groups : dict~str, nomenclature_group_model~
        +__new__(cls) storage_manager$
        +initialized : bool <<property>>
        +initialize() None
        +convert(obj: Any) Any
        +add_storage(obj) storage_model
        +get_storage(id) storage_model
        +remove_storage(id) None
        +storages : list~storage_model~ <<property>>
        +add_unit(obj) unit_model
        +get_unit(id) unit_model
        +remove_unit(id) None
        +units : list~unit_model~ <<property>>
        +add_nomenclature(obj) nomenclature_model
        +get_nomenclature(id) nomenclature_model
        +remove_nomenclature(id) None
        +nomenclatures : list~nomenclature_model~ <<property>>
        +add_group(obj) nomenclature_group_model
        +get_group(id) nomenclature_group_model
        +remove_group(id) None
        +groups : list~nomenclature_group_model~ <<property>>
        +find_by_name(collection, name) list
        +clear() None
        +reset_instance() None «classmethod»
        -_add_item(container, obj, type, kind) _T
        -_get_item(container, id) _T
        -_remove_item(container, id) None
        -_get_all(container) list~_T~
        -__to_dict(model) dict «static»
        -__create_initial_data() None
    }

    class abstract_model {
        <<abstract>>
        -_id : str
        -_name : str
        +id : str <<property>>
        +name : str <<property>>
        +__eq__(other) bool
    }

    class storage_model {
        -_address : str
        +address : str <<property>>
    }

    class unit_model {
        -_coefficient : float
        -_base_unit : unit_model
        +coefficient : float <<property>>
        +base_unit : unit_model <<property>>
    }

    class nomenclature_group_model {
        -_units : list~unit_model~
        +units : list~unit_model~ <<property>>
    }

    class nomenclature_model {
        -_full_name : str
        -_group : nomenclature_group_model
        -_unit : unit_model
        +full_name : str <<property>>
        +group : nomenclature_group_model <<property>>
        +unit : unit_model <<property>>
    }

    class arguments_exception {
        <<exception>>
        +message : str
        +param : str
    }

    abstract_manager <|-- settings_manager : наследование
    abstract_manager <|-- storage_manager : наследование
    abstract_model <|-- storage_model
    abstract_model <|-- unit_model
    abstract_model <|-- nomenclature_group_model
    abstract_model <|-- nomenclature_model

    storage_manager o--> "0..*" storage_model : хранит (id -> объект)
    storage_manager o--> "0..*" unit_model : хранит (id -> объект)
    storage_manager o--> "0..*" nomenclature_model : хранит (id -> объект)
    storage_manager o--> "0..*" nomenclature_group_model : хранит (id -> объект)

    unit_model o--> "0..1" unit_model : base_unit
    nomenclature_group_model o--> "0..*" unit_model : units
    nomenclature_model *-- "1" nomenclature_group_model : group
    nomenclature_model *-- "1" unit_model : unit

    settings_manager ..> arguments_exception : выбрасывает при ошибках
    storage_manager ..> arguments_exception : выбрасывает при ошибках
```

**Примечания:**
- `$` — статические/классовые атрибуты (реализация Singleton у `storage_manager`).
- У `-` членов — приватное состояние; публичный доступ только через свойства/методы.
- `convert` — шаблонный метод `abstract_manager`: у `settings_manager` преобразует
  настройки → типизированный `SimpleNamespace` по схеме; у `storage_manager` —
  модель ↔ канонический словарь (`type/id/name` + поля).

---

## 2. Диаграмма последовательности: Singleton + первый старт `storage_manager`

```mermaid
sequenceDiagram
    autonumber
    participant A as Поток/Клиент A
    participant B as Поток/Клиент B
    participant Cls as storage_manager (класс)
    participant Lk as __singleton_lock / _lock
    participant Init as initialize()
    participant Data as __create_initial_data()
    participant St as Хранилища (dict id→объект)

    A->>Cls: storage_manager()
    Cls->>Cls: __new__: __instance is None?
    Cls->>Lk: захват __singleton_lock
    Cls->>Cls: повторная проверка (double-checked locking)
    Cls->>Cls: super().__new__() → сохранить в __instance
    Lk-->>Cls: отпустить блокировку
    Cls-->>A: экземпляр синглтона

    A->>Cls: __init__()
    Cls->>Cls: __created == False
    Cls->>Lk: захват __singleton_lock
    Cls->>St: создать _storages/_units/_nomenclatures/_groups = {}
    Cls->>Cls: __created = True
    Lk-->>Cls: отпустить блокировку

    Note over A,Init: Первый старт приложения
    A->>Init: initialize()
    Init->>Init: проверка _initialized (идемпотентность)
    Init->>Data: __create_initial_data()
    Data->>St: add_unit ×6 (г, кг, мл, л, шт, дюжина)
    Data->>St: add_storage ×12 (центральный, цех, рестораны №1–№10)
    Data->>St: add_group ×4 (молочные, мясные, бакалея, напитки)
    Data->>St: add_nomenclature ×8 (молоко, сметана, говядина...)
    Init->>Init: _initialized = True

    B->>Cls: storage_manager()
    Cls-->>B: тот же самый экземпляр (__instance is not None)
    B->>Init: initialize() повторно
    Init-->>B: ничего не делает (данные уже созданы)
```
