import pytest

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.organization_model import organization_model, ownership_form
from Src.Models.unit_model import NAME_MAX_LENGTH

# Корректные значения реквизитов для тестов
VALID_INN_LEGAL = "7701234567"          # ИНН юрлица - 10 цифр
VALID_INN_IP = "770123456789"           # ИНН ИП - 12 цифр
VALID_BIK = "044525225"                 # БИК - 9 цифр
VALID_ACCOUNT = "40702810000000000123"  # Расчетный счет - 20 цифр


def test_organization_created_with_all_parameters_success():
    """
    Организация корректно создается со всеми параметрами:
    наименование, ИНН, БИК, счет, форма собственности, id.
    """
    # Действие
    org = organization_model(
        name="ООО Ромашка",
        inn=VALID_INN_LEGAL,
        bik=VALID_BIK,
        account=VALID_ACCOUNT,
        ownership_form_value=ownership_form.LIMITED_LIABILITY_COMPANY,
        id="org-1",
    )

    # Проверка
    assert isinstance(org, abstract_model)
    assert org.id == "org-1"
    assert org.name == "ООО Ромашка"
    assert org.inn == VALID_INN_LEGAL
    assert org.bik == VALID_BIK
    assert org.account == VALID_ACCOUNT
    assert org.ownership_form == ownership_form.LIMITED_LIABILITY_COMPANY


@pytest.mark.parametrize("inn", [VALID_INN_LEGAL, VALID_INN_IP])
def test_organization_accepts_ten_or_twelve_digit_inn_success(inn):
    """
    ИНН юридического лица (10 цифр) и индивидуального предпринимателя (12 цифр) допустимы.
    """
    # Действие
    org = organization_model("Ромашка", inn, VALID_BIK, VALID_ACCOUNT, ownership_form.PRIVATE)

    # Проверка
    assert org.inn == inn


def test_organization_accepts_string_ownership_form_success():
    """
    Форма собственности может быть задана строковым значением перечисления.
    """
    # Действие
    org = organization_model("Ромашка", VALID_INN_LEGAL, VALID_BIK, VALID_ACCOUNT,
                             "общество с ограниченной ответственностью")

    # Проверка
    assert org.ownership_form == ownership_form.LIMITED_LIABILITY_COMPANY


def test_setters_update_requisites_success():
    """
    Сеттеры реквизитов организации обновляют значения при корректных данных.
    """
    # Подготовка
    org = organization_model("Ромашка", VALID_INN_LEGAL, VALID_BIK, VALID_ACCOUNT,
                             ownership_form.STATE)

    # Действие
    org.inn = VALID_INN_IP
    org.bik = "044525999"
    org.account = "40702810000000000321"
    org.ownership_form = ownership_form.MUNICIPAL

    # Проверка
    assert org.inn == VALID_INN_IP
    assert org.bik == "044525999"
    assert org.account == "40702810000000000321"
    assert org.ownership_form == ownership_form.MUNICIPAL


@pytest.mark.parametrize("name", ["", "   ", None, 42])
def test_raise_arguments_exception_when_name_invalid(name):
    """
    Пустое или некорректное наименование организации вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        organization_model(name, VALID_INN_LEGAL, VALID_BIK, VALID_ACCOUNT, ownership_form.PRIVATE)


def test_raise_arguments_exception_when_name_longer_than_fifty():
    """
    Наименование организации ограничено 50 символами (обычное наименование).
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        organization_model("а" * (NAME_MAX_LENGTH + 1), VALID_INN_LEGAL, VALID_BIK,
                           VALID_ACCOUNT, ownership_form.PRIVATE)


@pytest.mark.parametrize("inn", ["", "123", "770123456", "77012345678", "770123456a", 7701234567])
def test_raise_arguments_exception_when_inn_invalid(inn):
    """
    Некорректный ИНН (не 10 и не 12 цифр) вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", inn, VALID_BIK, VALID_ACCOUNT, ownership_form.PRIVATE)


@pytest.mark.parametrize("bik", ["", "04452522", "0445252259", "04452522a", 44525225])
def test_raise_arguments_exception_when_bik_invalid(bik):
    """
    Некорректный БИК (не 9 цифр) вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", VALID_INN_LEGAL, bik, VALID_ACCOUNT, ownership_form.PRIVATE)


@pytest.mark.parametrize("account", ["", "4070281000000000012", "407028100000000001234",
                                     "4070281000000000012a"])
def test_raise_arguments_exception_when_account_invalid(account):
    """
    Некорректный номер расчетного счета (не 20 цифр) вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", VALID_INN_LEGAL, VALID_BIK, account, ownership_form.PRIVATE)


@pytest.mark.parametrize("form", ["", "неизвестная форма", 42, None])
def test_raise_arguments_exception_when_ownership_form_invalid(form):
    """
    Некорректная форма собственности вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", VALID_INN_LEGAL, VALID_BIK, VALID_ACCOUNT, form)
