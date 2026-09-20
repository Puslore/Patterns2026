from abc import ABC
from typing import Optional
import uuid


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
            raise ValueError('Идентификатор должен быть непустой строкой')
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
            raise ValueError('Имя должно быть непустой строкой')
        self._name = value.strip()
