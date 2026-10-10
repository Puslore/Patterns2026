from decimal import Decimal

from Src.Core.entity_model import entity_model
from Src.Core.validator import argument_exception, validator
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_ingredient_model import recipe_ingredient_model
from Src.Models.recipe_step_model import recipe_step_model


class recipe_model(entity_model):
    __category: str = ""
    __portions: int = 0
    __ingredients: list = None
    __steps: list = None

    def __init__(self) -> None:
        super().__init__()
        self.__ingredients = []
        self.__steps = []

    @property
    def category(self) -> str:
        return self.__category

    @category.setter
    def category(self, value: str):
        validator.validate(value, str)
        self.__category = value.strip()

    @property
    def portions(self) -> int:
        return self.__portions

    @portions.setter
    def portions(self, value: int):
        validator.validate(value, int)
        if value <= 0:
            raise argument_exception("Количество порций должно быть положительным")
        self.__portions = value

    @property
    def ingredients(self) -> list:
        return list(self.__ingredients)

    @property
    def steps(self) -> list:
        return list(self.__steps)

    @property
    def gross_weight_grams(self) -> Decimal:
        return sum((item.gross_weight_grams for item in self.__ingredients), Decimal("0"))

    @property
    def net_weight_grams(self) -> Decimal:
        return sum((item.net_weight_grams for item in self.__ingredients), Decimal("0"))

    def add_ingredient(self, ingredient: recipe_ingredient_model):
        validator.validate(ingredient, recipe_ingredient_model)
        if ingredient.recipe is not None and self.__contains_recipe(ingredient.recipe, self):
            raise argument_exception("Вложенный рецепт образует циклическую зависимость")
        if ingredient in self.__ingredients:
            raise argument_exception("Ингредиент уже добавлен в рецепт")
        self.__ingredients.append(ingredient)

    def remove_ingredient(self, ingredient: recipe_ingredient_model):
        validator.validate(ingredient, recipe_ingredient_model)
        if ingredient not in self.__ingredients:
            raise argument_exception("Ингредиент отсутствует в рецепте")
        self.__ingredients.remove(ingredient)

    def add_step(self, step: recipe_step_model):
        validator.validate(step, recipe_step_model)
        if any(existing.number == step.number for existing in self.__steps):
            raise argument_exception("Этап с таким номером уже существует")
        self.__steps.append(step)
        self.__steps.sort(key=lambda item: item.number)

    @staticmethod
    def __contains_recipe(candidate, target) -> bool:
        if candidate is target:
            return True
        if not isinstance(candidate, recipe_model):
            return False
        return any(item.recipe is not None and
                   recipe_model.__contains_recipe(item.recipe, target)
                   for item in candidate.ingredients)

    @staticmethod
    def create_borsch():
        grams = range_model.create_gram()
        pieces = range_model.create_piece()
        milliliters = range_model.create_milliliter()
        groups = {}

        def product(name, unit=grams, category="Ингредиенты"):
            if category not in groups:
                groups[category] = group_model.create(category)
            return nomenclature_model.create_ingredient(name, groups[category], unit)

        beet = product("Свёкла", category="Овощи")
        oil = product("Масло подсолнечное", milliliters, "Бакалея")
        tomato_paste = product("Томатная паста", category="Бакалея")
        sugar = product("Сахар", category="Бакалея")
        vinegar = product("Уксус 9%", milliliters, "Бакалея")

        saute = recipe_model()
        saute.name = "Пассеровка свекольная"
        saute.category = "Полуфабрикаты"
        saute.portions = 10
        for item, gross, net in (
                (beet, 800, 720),
                (oil, 92, 92),
                (tomato_paste, 150, 150),
                (sugar, 30, 30),
                (vinegar, 20, 20)):
            saute.add_ingredient(recipe_ingredient_model.create_for_nomenclature(item, gross, net))
        saute.add_step(recipe_step_model.create(
            1, "Пассеровка свёклы",
            "Свёклу очистить и нарезать. Пассеровать в масле, добавить томатную "
            "пасту, сахар и уксус; тушить до готовности.", 20))

        result = recipe_model()
        result.name = "Борщ столичный"
        result.category = "Супы (первые блюда)"
        result.portions = 10
        result.add_ingredient(recipe_ingredient_model.create_for_recipe(saute))

        other_ingredients = (
            ("Морковь", 400, 360, grams, "Овощи"),
            ("Картофель", 600, 510, grams, "Овощи"),
            ("Капуста белокочанная", 500, 450, grams, "Овощи"),
            ("Лук репчатый", 200, 180, grams, "Овощи"),
            ("Говядина (на кости)", 700, 500, grams, "Мясные продукты"),
            ("Вода", 3500, 3500, grams, "Вспомогательные продукты"),
            ("Соль пищевая мелкая", 45, 45, grams, "Бакалея"),
            ("Перец черный молотый", 5, 5, grams, "Бакалея"),
            ("Лавровый лист", 1, 1, pieces, "Бакалея"),
            ("Сметана 20%", 200, 200, grams, "Молочные продукты"),
            ("Зелень петрушки", 30, 27, grams, "Овощи"))
        for name, gross, net, unit, category in other_ingredients:
            item = product(name, unit, category)
            result.add_ingredient(recipe_ingredient_model.create_for_nomenclature(item, gross, net))

        for step in (
                recipe_step_model.create(
                    1, "Подготовка бульона",
                    "Говядину промыть, залить водой, довести до кипения и снять пену. "
                    "Варить до готовности, мясо отделить от костей, бульон процедить.", 60),
                recipe_step_model.create(
                    2, "Подготовка овощей",
                    "Очистить и нарезать морковь, картофель, капусту и лук. "
                    "Морковь и лук отдельно пассеровать до золотистого цвета. "
                    "Приготовить свекольную пассеровку по отдельной карте.", 20),
                recipe_step_model.create(
                    3, "Варка борща",
                    "В бульоне сварить картофель и капусту, добавить овощи и "
                    "пассеровку, приправить солью, перцем и лавровым листом. "
                    "Прогреть без кипения; лавровый лист удалить.", 25),
                recipe_step_model.create(
                    4, "Подача",
                    "На порцию борща добавить сметану и зелень. Температура подачи "
                    "не ниже 65 °C.")):
            result.add_step(step)
        return result
