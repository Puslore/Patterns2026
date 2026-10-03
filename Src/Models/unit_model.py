from typing import Optional

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception

# Максимальная длина обычного наименования сущности - 50 символов.
NAME_MAX_LENGTH = 50


class unit_model(abstract_model):
    """
    Модель `Единица измерения`.

    Простая доменная сущность, описывающая единицу измерения и её связь
    с базовой единицей измерения через коэффициент пересчета.

    Пример:
        base_unit = unit_model("грамм", 1)          # базовая единица: coefficient == 1
        kg = unit_model("кг", 1000, base_unit)      # 1 кг = 1000 базовых единиц (грамм)

    Правила:
        - Если базовая единица не указана, сущность сама считается базовой
          (коэффициент пересчета обязан быть равен 1).
        - Коэффициент пересчета должен быть положительным числом.
        - Цепочка базовых единиц не должна содержать циклов.
    """

    # Наименование сущности. Обычное ограничение - 50 символов.
    _name_max_length: int = NAME_MAX_LENGTH

    # Коэффициент пересчета в базовую единицу измерения.
    _coefficient: float = 1.0

    # Базовая единица измерения, относительно которой задан коэффициент. None для базовых единиц.
    _base_unit: Optional['unit_model'] = None

    def __init__(self, name: str, coefficient: float = 1.0,
                 base_unit: Optional['unit_model'] = None, id: Optional[str] = None) -> None:
        """
        Инициализация единицы измерения.
        :param name: Наименование единицы измерения (не длиннее 50 символов)
        :param coefficient: Коэффициент пересчета в базовую единицу измерения
        :param base_unit: Базовая единица измерения (None - если единица сама является базовой)
        :param id: Необязательный идентификатор сущности
        """
        self.name = name
        self.base_unit = base_unit
        self.coefficient = coefficient
        if id is not None:
            self.id = id

    @property
    def coefficient(self) -> float:
        """
        Возвращает коэффициент пересчета в базовую единицу измерения.
        """
        return self._coefficient

    @coefficient.setter
    def coefficient(self, value: float) -> None:
        """
        Установка коэффициента пересчета.
        Допускаются только положительные числа. Для базовой единицы коэффициент обязан равняться 1.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise arguments_exception('Коэффициент пересчета должен быть положительным числом', 'coefficient')
        if value <= 0:
            raise arguments_exception('Коэффициент пересчета должен быть больше нуля', 'coefficient')
        if self._base_unit is None and value != 1:
            raise arguments_exception(
                'Базовая единица измерения имеет коэффициент пересчета равный 1', 'coefficient')
        self._coefficient = float(value)

    @property
    def base_unit(self) -> Optional['unit_model']:
        """
        Возвращает базовую единицу измерения. None - если единица сама является базовой.
        """
        return self._base_unit

    @base_unit.setter
    def base_unit(self, value: Optional['unit_model']) -> None:
        """
        Установка базовой единицы измерения.
        Проверяется тип значения, корректность её коэффициента и отсутствие циклов в цепочке.
        """
        if value is None:
            self._base_unit = None
            return
        if not isinstance(value, unit_model):
            raise arguments_exception('Базовая единица должна быть экземпляром unit_model', 'base_unit')
        if value is self:
            raise arguments_exception('Единица измерения не может быть базовой для самой себя', 'base_unit')
        if value.has_cycle_to(self):
            raise arguments_exception('Цепочка базовых единиц не должна содержать циклов', 'base_unit')
        if value.coefficient <= 0:
            raise arguments_exception('Некорректный коэффициент у базовой единицы измерения', 'base_unit')
        self._base_unit = value

    @property
    def is_base(self) -> bool:
        """
        Признак базовой единицы измерения (не ссылается ни на какую другую).
        """
        return self._base_unit is None

    def has_cycle_to(self, target: 'unit_model') -> bool:
        """
        Проверяет, встречается ли целевая единица в цепочке базовых единиц начиная с этой.
        Используется для предотвращения зацикливания при установке base_unit.
        :param target: Единица измерения, наличие которой проверяется в цепочке
        :return: True, если целевая единица уже присутствует в цепочке
        """
        visited = set()
        current: Optional['unit_model'] = self
        while current is not None:
            if current is target:
                return True
            if id(current) in visited:
                return False
            visited.add(id(current))
            current = current._base_unit
        return False

    def to_base(self, amount: float = 1.0) -> float:
        """
        Пересчитывает количество в данной единице измерения к базовой единице цепочки.
        :param amount: Количество в текущей единице измерения
        :return: Количество в базовой единице измерения
        """
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise arguments_exception('Количество должно быть числом', 'amount')
        result = float(amount) * self._coefficient
        current = self._base_unit
        while current is not None:
            result *= current._coefficient
            current = current._base_unit
        return result

    @property
    def name(self) -> Optional[str]:
        """
        Возвращает наименование единицы измерения.
        """
        return getattr(self, '_name', None)

    @name.setter
    def name(self, value: str) -> None:
        """
        Установка наименования. Обычное ограничение поля `наименование` - 50 символов.
        """
        super(unit_model, type(self)).name.fset(self, value)
        if len(self._name) > self._name_max_length:
            raise arguments_exception(
                f'Наименование не может быть длиннее {self._name_max_length} символов', 'name')
