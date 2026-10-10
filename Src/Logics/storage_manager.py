from Src.Core.abstract_manager import abstract_manager
from Src.Models.storage_model import storage_model
from Src.Models.settings_model import settings_model
from Src.Models.recipe_model import recipe_model
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
    Ключ для единц измерений
    """
    @staticmethod
    def range_key():
        return "range_model"
    

    """
    Ключ для категорий
    """
    @staticmethod
    def group_key():
        return "group_model"
    
    """
    Ключ для склада
    """
    @staticmethod
    def storage_key():
        return "storage_key"

    """
    Ключ для номенклатуры
    """
    @staticmethod
    def nomenclature_key():
        return "nomenclature_model"

    @staticmethod
    def recipe_key():
        return "recipe_model"

    """
    Получить список всех ключей
    Источник: https://github.com/Alyona1619
    """
    @staticmethod
    def keys() -> list:
        result = []
        methods = [method for method in dir(storage_manager) if
                    callable(getattr(storage_manager, method)) and method.endswith('_key')]
        for method in methods:
            key = getattr(storage_manager, method)()
            result.append(key)

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
        keys = storage_manager.keys()
        for key in keys:
            self.__data[ key ] = []
        

    """
    Генерация данных
    """        
    def build(self):

        if self.__settings.first_start == False or self.is_loaded == True:
            return False
        
        recipe = recipe_model.create_borsch()
        nomenclatures = []
        groups = []
        ranges = []

        def collect_recipe_data(current_recipe):
            for line in current_recipe.ingredients:
                if line.recipe is not None:
                    collect_recipe_data(line.recipe)
                    continue
                item = line.nomenclature
                if item not in nomenclatures:
                    nomenclatures.append(item)
                if item.group not in groups:
                    groups.append(item.group)
                if item.range not in ranges:
                    ranges.append(item.range)

        collect_recipe_data(recipe)
        self.data[ storage_manager.range_key() ] = ranges
        self.data[ storage_manager.group_key() ] = groups
        self.data[ storage_manager.storage_key() ] = [storage_model.create_main()]
        self.data[ storage_manager.nomenclature_key() ] = nomenclatures
        self.data[ storage_manager.recipe_key() ] = [recipe]
        self.is_loaded = True

        return True

        

