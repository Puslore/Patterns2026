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
from Src.Logics.storage_reposity import storage_repository

"""
Реализация менеджера для управления и кеширования доменных сущностей
"""
class storage_manager(abstract_manager):
    # Набор данных
    __data = {}
    # Текущие настройки
    __settings:settings_model = None
    # Репозиторий
    __repository:storage_repository = None

    """
    Единица измерений
    """
    @staticmethod
    def range_key():
        return "3 range_model"
    

    """
    Категория
    """
    @staticmethod
    def group_key():
        return "1 group_model"
    
    """
    Склад
    """
    @staticmethod
    def storage_key():
        return "2 storage_model"

    """
    Номенклатура
    """
    @staticmethod
    def nomenclature_key():
        return "4 nomenclature_model"

    """
    Рецепты
    """
    @staticmethod
    def receipt_key():
        return "6 receipt_model"

    """
    Ингредиенты
    """
    @staticmethod
    def ingredient_key():
        return "5 ingredient_model"


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
        validator.validate(settings, settings_model)
        self.__settings = settings
        
        keys = storage_manager.domains().keys()
        for key in keys:
            self.__data[ key ] = []

        self.__repository = storage_repository()    

    """
    Генерация данных
    """        
    def build(self):

        if self.__settings.first_start == False or self.is_loaded == True:
            return False
        
        # Единицы измерения
        range_killogramm = range_model.create_killogramm()

        range_item = range_model()
        range_item.name = "Штуки"

        items =  [range_killogramm.base, range_killogramm, range_item]
        self.data[ storage_manager.range_key() ] = items
        self.__repository.registry_range ( items )

        # Группы
        group = group_model.create_default_group()
        items =  [group]
        self.data[ storage_manager.group_key() ] = items
        self.__repository.registry_range( items )

        # Склады
        storage = storage_model()
        storage.name = "Основной склад"
        storage.address = "Иркутск, ул. Высокого Полета, д.100"
        items = [storage]
        self.data[ storage_manager.storage_key() ] = items
        self.__repository.registry_range( items )

        # Номенклатура
        nomenclature_flour = nomenclature_model()
        nomenclature_flour.name = "Пшеничная мука"
        nomenclature_flour.group = group
        nomenclature_flour.range = range_killogramm

        nomenclature_sugar = nomenclature_model()
        nomenclature_sugar.name = "Сахар"
        nomenclature_sugar.group = group
        nomenclature_sugar.range = range_killogramm

        nomenclature_oil = nomenclature_model()
        nomenclature_oil.name = "Сливочное масло"
        nomenclature_oil.group = group
        nomenclature_oil.range = range_killogramm

        nomenclature_egg = nomenclature_model()
        nomenclature_egg.name = "Яйцо (шт)"
        nomenclature_egg.group = group
        nomenclature_egg.range = range_item

        nomenclature_vanilin = nomenclature_model()
        nomenclature_vanilin.name = "Ванилин"
        nomenclature_vanilin.group = group
        nomenclature_vanilin.range = range_killogramm.base

        items = [nomenclature_flour, nomenclature_sugar, nomenclature_oil, nomenclature_egg, nomenclature_vanilin]
        self.data[ storage_manager.nomenclature_key() ] = items
        self.__repository.registry_range( items )

        # Создание рецепта "Вафли хрустящие в вафельнице" (10 порций)
        receipt = receipt_model()

        # Ингредиент 1: Пшеничная мука (100 гр)
        ingredient_flour = ingredient_model()
        ingredient_flour.name = "Пшеничная мука"
        ingredient_flour.group = group
        ingredient_flour.range = range_killogramm
        ingredient_flour.brutto = 100
        ingredient_flour.netto = 100
        receipt.add(ingredient_flour)

        # Ингредиент 2: Сахар (80 гр)
        ingredient_sugar = ingredient_model()
        ingredient_sugar.name = "Сахар"
        ingredient_sugar.group = group
        ingredient_sugar.range = range_killogramm
        ingredient_sugar.brutto = 80
        ingredient_sugar.netto = 80
        receipt.add(ingredient_sugar)

        # Ингредиент 3: Сливочное масло (70 гр)
        ingredient_butter = ingredient_model()
        ingredient_butter.name = "Сливочное масло"
        ingredient_butter.group = group
        ingredient_butter.range = range_killogramm
        ingredient_butter.brutto = 70
        ingredient_butter.netto = 70
        receipt.add(ingredient_butter)

        # Ингредиент 4: Яйца (1 шт)
        ingredient_egg = ingredient_model()
        ingredient_egg.name = "Яйца"
        ingredient_egg.group = group
        ingredient_egg.range = range_item
        ingredient_egg.brutto = 1
        ingredient_egg.netto = 1
        receipt.add(ingredient_egg)

        # Ингредиент 5: Ванилин (5 гр)
        ingredient_vanilin = ingredient_model()
        ingredient_vanilin.name = "Ванилин"
        ingredient_vanilin.group = group
        ingredient_vanilin.range = range_killogramm.base
        ingredient_vanilin.brutto = 5
        ingredient_vanilin.netto = 5
        receipt.add(ingredient_vanilin)

        # Сохранение рецепта в кеш
        items = receipt.items
        self.data[ storage_manager.ingredient_key()] = items
        self.__repository.registry_range( items )
        
        items =  [receipt]
        self.data[ storage_manager.receipt_key() ] = items
        self.__repository.registry_range( items )

        return True

    """
    Репозиторий с данными
    """
    @property
    def repository(self) -> storage_repository:
        return self.__repository
   
        




