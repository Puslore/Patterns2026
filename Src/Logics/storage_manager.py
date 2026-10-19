from Src.Core.abstract_manager import abstract_manager
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.settings_model import settings_model
from Src.Core.validator import validator

"""
Реализация менеджера для управления и кеширования доменных сущностей
"""
class storage_manager(abstract_manager):
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
        return "storage_key"

    """
    Номенклатура
    """
    @staticmethod
    def nomenclature_key():
        return "nomenclature_model"


    @staticmethod
    def domains() -> dict:
        """
        Возвращает словарь всех доступных ключей и их описаний.
        Ключ — значение, возвращаемое методом (например, "nomenclature_model").
        Значение — описание из docstring метода (например, "Номенклатура").
        """
        result = {}
        
        # Получаем список имен всех статических методов, заканчивающихся на '_key'
        method_names = [
            name for name in dir(storage_manager) 
            if callable(getattr(storage_manager, name)) and name.endswith('_key')
        ]

        for method_name in method_names:
            # Получаем сам объект метода
            method = getattr(storage_manager, method_name)
            
            # Получаем значение ключа (например, "nomenclature_model")
            key_value = method()
            
            # Получаем описание из документации (первая строка docstring)
            docstring = method.__doc__
            description = docstring.strip().split('\n')[0] if docstring else method_name
            
            result[key_value] = description
            
        return result
    


    """
    Получить набор данных
    """
    @property
    def data(self):
        return self.__data



    """
    Конструктор
    """
    def __init__(self, settings:settings_model):
        validator.validate(settings, settings_model)
        self.__settings = settings
        
        keys = storage_manager.domains().keys()
        for key in keys:
            self.__data[ key ] = []
        

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

        self.data[ storage_manager.range_key() ] = [range_killogramm.base, range_killogramm, range_item]

        # Группы
        group = group_model.create_default_group()
        self.data[ storage_manager.group_key() ] = [group]

        # Склады
        storage = storage_model()
        storage.name = "Основной склад"
        storage.address = "Иркутск, ул. Высокого Полета, д.100"

        self.data[ storage_manager.storage_key() ] = [storage]

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

        self.data[ storage_manager.nomenclature_key() ] = [nomenclature_flour, nomenclature_sugar, nomenclature_oil, nomenclature_egg, nomenclature_vanilin]

        # TODO: По аналогии добавить Default рецепт

        return True

        




