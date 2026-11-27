from Src.Core.abstract_model import abstact_model
from Src.Core.common import common
from Src.Core.entity_model import entity_model
from Src.Core.validator import validator, operation_exception


class storage_repository:
    """
    Репозиторий для хранения списка объектов и счетчика связей
    """

    # Исходный набор данных. Ключ - GUID, значение - abstract_model
    __data: dict = {}
    # Счетчик ссылок. Ключ - GUID, значение - число ссылок
    __counts: dict = {}

    def __init__(self):
        """
        Инициализировать репозиторий
        """
        self.__data = {}
        self.__counts = {}

    def registry(self, source: abstact_model) -> None:
        """
        Зарегистрировать доменный объект и его вложенные сущности
        """
        validator.validate(source, abstact_model)

        # Регистрируем основной объект
        self.__data[source.unique_code] = source
        if source.unique_code in self.__counts.keys():
            self.__counts[source.unique_code] += 1
        else:
            self.__counts[source.unique_code] = 0

        # Регистрируем вложения
        fields = common.get_fields(source, False)
        for field in fields:
            value = getattr(source, field, None)
            if isinstance(value, (abstact_model, entity_model)):
                self.registry(value)

    def registry_range(self, items: list) -> None:
        """
        Зарегистрировать сразу же несколько объектов
        """
        validator.validate(items, list)
        for item in items:
            self.registry(item)

    def get(self, source: str) -> abstact_model:
        """
        Получить объект по уникальному коду
        """
        validator.validate(source, str)

        if source in self.__data.keys():
            return self.__data.get(source)
        else:
            raise operation_exception(f"Не найдена доменная сущность по коду : {source}!")

    def can_delete(self, source: abstact_model) -> bool:
        """
        Проверить возможность удаления
        """
        validator.validate(source, abstact_model)

        try:
            self.get(source.unique_code)

            if self.__counts.get(source.unique_code, 0) > 0:
                # Есть связи
                return False
            else:
                return True
        except Exception:
            # Не найдено
            return False

    def delete(self, source: abstact_model) -> None:
        """
        Удалить сущность из счетчиков
        """
        validator.validate(source, abstact_model)
        if not self.can_delete(source):
            raise operation_exception(f"Невозможно удалить запись {source.unique_code}!")

        self.__data.pop(source.unique_code, None)
        self.__counts.pop(source.unique_code, None)

    @property
    def data(self) -> dict:
        """
        Исходный набор данных
        """
        return self.__data

    @property
    def counts(self) -> dict:
        """
        Исходный набор счетчиков
        """
        return self.__counts
