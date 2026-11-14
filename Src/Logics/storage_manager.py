from Src.Core.abstract_manager import abstract_manager
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.settings_model import settings_model
from Src.Core.validator import validator
from Src.Models.ingredient_model import ingredient_model
from Src.Models.receipt_model import receipt_model
from Src.Core.common import common

"""
Реализация менеджера для управления и кеширования доменных сущностей
"""
class storage_manager(abstract_manager):
    """Менеджер, формирующий начальный набор доменных данных."""

    # Набор данных
    __data = {}
    # Текущие настройки
    __settings:settings_model = None

    """
    Единица измерений
    """
    @staticmethod
    def range_key():
        return "range_model"

    """
    Категория
    """
    @staticmethod
    def group_key():
        return "group_model"

    """
    Склад
    """
    @staticmethod
    def storage_key():
        return "storage_model"

    """
    Номенклатура
    """
    @staticmethod
    def nomenclature_key():
        return "nomenclature_model"

    """
    Рецепты
    """
    @staticmethod
    def receipt_key():
        return "receipt_model"

    @staticmethod
    def recipe_key():
        """Вернуть ключ коллекции рецептов в наборе данных (алиас)."""
        return "receipt_model"

    """
    Получить список всех ключей и описания к ним
    """
    @staticmethod
    def domains() -> dict:
        return common.domains( storage_manager )

    """
    Получить набор данных
    """
    @property
    def data(self):
        return self.__data

    # Singletone
    def __new__(cls, settings:settings_model):
        if not hasattr(cls, 'instance'):
            cls.instance = super(storage_manager, cls).__new__(cls)
        return cls.instance 

    """
    Конструктор
    """
    def __init__(self, settings:settings_model):
        """Создать менеджер для указанных настроек приложения."""
        validator.validate(settings, settings_model)
        self.__settings = settings
        self.is_loaded = False

        keys = storage_manager.domains().keys()
        for key in keys:
            self.__data[ key ] = []

    """
    Генерация данных
    """
    def build(self):
        """Сформировать доменные данные при первом запуске."""

        if self.__settings.first_start == False or self.is_loaded == True:
            return False

        # Единицы измерения
        range_killogramm = range_model.create_killogramm()
        range_item = range_model.create_thing()

        self.data[ storage_manager.range_key() ] = [range_killogramm.base, range_killogramm, range_item]

        # Группы номенклатуры
        group_default = group_model.create_default_group()
        group_vegetables = group_model.create("Овощи")
        group_meat = group_model.create("Мясные продукты")
        group_grocery = group_model.create("Бакалея")
        group_dairy = group_model.create("Молочные продукты")
        self.data[ storage_manager.group_key() ] = [group_default, group_vegetables, group_meat, group_grocery, group_dairy]

        # Склады
        storage = storage_model()
        storage.name = "Основной склад"
        storage.address = "Иркутск, ул. Высокого Полета, д.100"
        self.data[ storage_manager.storage_key() ] = [storage]

        # Номенклатура
        nomenclature_beet = nomenclature_model()
        nomenclature_beet.name = "Свёкла"
        nomenclature_beet.group = group_vegetables
        nomenclature_beet.range = range_killogramm

        nomenclature_potato = nomenclature_model()
        nomenclature_potato.name = "Картофель"
        nomenclature_potato.group = group_vegetables
        nomenclature_potato.range = range_killogramm

        nomenclature_cabbage = nomenclature_model()
        nomenclature_cabbage.name = "Капуста белокочанная"
        nomenclature_cabbage.group = group_vegetables
        nomenclature_cabbage.range = range_killogramm

        nomenclature_carrot = nomenclature_model()
        nomenclature_carrot.name = "Морковь"
        nomenclature_carrot.group = group_vegetables
        nomenclature_carrot.range = range_killogramm

        nomenclature_onion = nomenclature_model()
        nomenclature_onion.name = "Лук репчатый"
        nomenclature_onion.group = group_vegetables
        nomenclature_onion.range = range_killogramm

        nomenclature_beef = nomenclature_model()
        nomenclature_beef.name = "Говядина"
        nomenclature_beef.group = group_meat
        nomenclature_beef.range = range_killogramm

        nomenclature_oil = nomenclature_model()
        nomenclature_oil.name = "Масло подсолнечное"
        nomenclature_oil.group = group_grocery
        nomenclature_oil.range = range_killogramm

        nomenclature_tomato = nomenclature_model()
        nomenclature_tomato.name = "Томатная паста"
        nomenclature_tomato.group = group_grocery
        nomenclature_tomato.range = range_killogramm

        nomenclature_sugar = nomenclature_model()
        nomenclature_sugar.name = "Сахар"
        nomenclature_sugar.group = group_grocery
        nomenclature_sugar.range = range_killogramm

        nomenclature_salt = nomenclature_model()
        nomenclature_salt.name = "Соль"
        nomenclature_salt.group = group_grocery
        nomenclature_salt.range = range_killogramm

        nomenclature_flour = nomenclature_model()
        nomenclature_flour.name = "Пшеничная мука"
        nomenclature_flour.group = group_default
        nomenclature_flour.range = range_killogramm

        nomenclature_butter = nomenclature_model()
        nomenclature_butter.name = "Сливочное масло"
        nomenclature_butter.group = group_dairy
        nomenclature_butter.range = range_killogramm

        nomenclature_egg = nomenclature_model()
        nomenclature_egg.name = "Яйцо (шт)"
        nomenclature_egg.group = group_default
        nomenclature_egg.range = range_item

        nomenclature_vanilin = nomenclature_model()
        nomenclature_vanilin.name = "Ванилин"
        nomenclature_vanilin.group = group_default
        nomenclature_vanilin.range = range_killogramm.base

        self.data[ storage_manager.nomenclature_key() ] = [
            nomenclature_beet,
            nomenclature_potato,
            nomenclature_cabbage,
            nomenclature_carrot,
            nomenclature_onion,
            nomenclature_beef,
            nomenclature_oil,
            nomenclature_tomato,
            nomenclature_sugar,
            nomenclature_salt,
            nomenclature_flour,
            nomenclature_butter,
            nomenclature_egg,
            nomenclature_vanilin
        ]

        # Создание рецепта "Борщ столичный" (10 порций)
        receipt = receipt_model()
        receipt.name = "Борщ столичный"
        receipt.comments = "Технологическая карта приготовления блюда Борщ столичный (сеть ресторанов Ромашка)"

        # Основа для пассеровки - свёкла
        ingredient_beet_base = ingredient_model()
        ingredient_beet_base.name = "Свёкла (для пассеровки)"
        ingredient_beet_base.group = group_vegetables
        ingredient_beet_base.range = range_killogramm
        ingredient_beet_base.brutto = 800
        ingredient_beet_base.netto = 720

        # Полуфабрикат "Пассеровка свекольная" (блюдо в блюде со ссылкой base)
        ingredient_passerovka = ingredient_model()
        ingredient_passerovka.name = "Пассеровка свекольная"
        ingredient_passerovka.group = group_vegetables
        ingredient_passerovka.range = range_killogramm
        ingredient_passerovka.base = ingredient_beet_base
        ingredient_passerovka.brutto = 292
        ingredient_passerovka.netto = 292
        receipt.add(ingredient_passerovka)

        # Ингредиент 2: Картофель (600 гр брутто / 510 гр нетто)
        ingredient_potato = ingredient_model()
        ingredient_potato.name = "Картофель"
        ingredient_potato.group = group_vegetables
        ingredient_potato.range = range_killogramm
        ingredient_potato.brutto = 600
        ingredient_potato.netto = 510
        receipt.add(ingredient_potato)

        # Ингредиент 3: Капуста белокочанная (500 гр брутто / 450 гр нетто)
        ingredient_cabbage = ingredient_model()
        ingredient_cabbage.name = "Капуста белокочанная"
        ingredient_cabbage.group = group_vegetables
        ingredient_cabbage.range = range_killogramm
        ingredient_cabbage.brutto = 500
        ingredient_cabbage.netto = 450
        receipt.add(ingredient_cabbage)

        # Ингредиент 4: Морковь (400 гр брутто / 360 гр нетто)
        ingredient_carrot = ingredient_model()
        ingredient_carrot.name = "Морковь"
        ingredient_carrot.group = group_vegetables
        ingredient_carrot.range = range_killogramm
        ingredient_carrot.brutto = 400
        ingredient_carrot.netto = 360
        receipt.add(ingredient_carrot)

        # Ингредиент 5: Лук репчатый (200 гр брутто / 180 гр нетто)
        ingredient_onion = ingredient_model()
        ingredient_onion.name = "Лук репчатый"
        ingredient_onion.group = group_vegetables
        ingredient_onion.range = range_killogramm
        ingredient_onion.brutto = 200
        ingredient_onion.netto = 180
        receipt.add(ingredient_onion)

        # Ингредиент 6: Говядина (700 гр брутто / 500 гр нетто)
        ingredient_beef = ingredient_model()
        ingredient_beef.name = "Говядина (на кости)"
        ingredient_beef.group = group_meat
        ingredient_beef.range = range_killogramm
        ingredient_beef.brutto = 700
        ingredient_beef.netto = 500
        receipt.add(ingredient_beef)

        # Сохранение рецепта в кеш
        self.data[ storage_manager.receipt_key() ] = [receipt]
        self.is_loaded = True

        return True
