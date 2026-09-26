from abc import ABC
from typing import Optional
import uuid
from Src.Core.exception import arguments_exception


class abstract_model(ABC):
    """
    Абстрактный класс для сущности.
    """

    # Внутренний идентификатор сущности. До первой генерации может быть None.
    _id: Optional[str] = None
    
    # Наименование сущности. По умолчанию None.
    _name: Optional[str] = None

    @property
    def id(self) -> str:
        """
        Возвращает id сущности.
        Если не задан, то генерируется автоматически при первом обращении.
        """

        if self._id is not None:
            return self._id

        self._id = str(uuid.uuid4())
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        """
        Установка идентификатора объекта.
        """
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception('Идентификатор должен быть непустой строкой', 'id')
        self._id = value.strip()

    @property
    def name(self) -> Optional[str]:
        """
        Возвращает наименование сущности.
        """
        return getattr(self, '_name', None)

    @name.setter
    def name(self, value: str) -> None:
        """
        Установка наименования сущности.
        """
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception('Имя должно быть непустой строкой', 'name')
        self._name = value.strip()
    
    def __eq__(self, other: object) -> bool:
        """
        Сравнение сущностей по идентификатору id.
        """
        if not isinstance(other, abstract_model):
            return False
        return self.id == other.id
