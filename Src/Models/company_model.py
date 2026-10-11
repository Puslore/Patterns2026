from Src.Core.entity_model import entity_model
from Src.Core.validator import validator


class company_model(entity_model):
    """Реквизиты организации, используемые в настройках приложения."""

    __inn: int = 0
    __bic: str = ""
    __corr_account: str = ""
    __account: str = ""
    __ownership: str = ""

    @property
    def inn(self) -> int:
        """Вернуть ИНН организации."""
        return self.__inn

    @inn.setter
    def inn(self, value: int) -> None:
        """Сохранить ИНН, представленный целым числом."""
        validator.validate(value, int, 12)
        self.__inn = value

    @property
    def bik(self) -> str:
        """Вернуть банковский идентификационный код."""
        return self.__bic

    @bik.setter
    def bik(self, value: str) -> None:
        """Сохранить БИК длиной не более девяти символов."""
        validator.validate(value, str, 9)
        self.__bic = value.strip()

    @property
    def corr_account(self) -> str:
        """Вернуть корреспондентский банковский счет."""
        return self.__corr_account

    @corr_account.setter
    def corr_account(self, value: str) -> None:
        """Сохранить корреспондентский счет без потери ведущих нулей."""
        validator.validate(value, str, 20)
        self.__corr_account = value.strip()

    @property
    def account(self) -> str:
        """Вернуть банковский счет организации."""
        return self.__account

    @account.setter
    def account(self, value: str) -> None:
        """Сохранить банковский счет без потери ведущих нулей."""
        validator.validate(value, str, 20)
        self.__account = value.strip()

    @property
    def ownership(self) -> str:
        """Вернуть вид собственности организации."""
        return self.__ownership

    @ownership.setter
    def ownership(self, value: str) -> None:
        """Сохранить вид собственности длиной не более пяти символов."""
        validator.validate(value, str, 5)
        self.__ownership = value.strip()

