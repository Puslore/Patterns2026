from decimal import Decimal, InvalidOperation

from Src.Core.entity_model import entity_model
from Src.Core.validator import argument_exception, validator
from Src.Models.nomenclature_model import nomenclature_model


class recipe_ingredient_model(entity_model):
    """Строка рецепта, ссылающаяся на продукт или вложенный рецепт."""

    __nomenclature: nomenclature_model = None
    __recipe: object = None
    __gross_weight_grams: Decimal = Decimal("0")
    __net_weight_grams: Decimal = Decimal("0")

    @property
    def nomenclature(self) -> nomenclature_model:
        """Вернуть номенклатуру ингредиента, если строка содержит продукт."""
        return self.__nomenclature

    @property
    def recipe(self):
        """Вернуть вложенный рецепт-полуфабрикат, если он задан."""
        return self.__recipe

    @property
    def gross_weight_grams(self) -> Decimal:
        """Вернуть вес брутто продукта или рассчитанный вес вложенного рецепта."""
        if self.__recipe is not None:
            return self.__recipe.gross_weight_grams
        return self.__gross_weight_grams

    @property
    def net_weight_grams(self) -> Decimal:
        """Вернуть вес нетто продукта или рассчитанный вес вложенного рецепта."""
        if self.__recipe is not None:
            return self.__recipe.net_weight_grams
        return self.__net_weight_grams

    @classmethod
    def create_for_nomenclature(cls, nomenclature: nomenclature_model,
                                gross_weight_grams, net_weight_grams):
        """Создать строку для продукта с заданными весами брутто и нетто."""
        validator.validate(nomenclature, nomenclature_model)
        return cls.__create(nomenclature, None, gross_weight_grams, net_weight_grams)

    @classmethod
    def create_for_recipe(cls, recipe):
        """Создать строку для полуфабриката с вычисляемым весом."""
        from Src.Models.recipe_model import recipe_model

        validator.validate(recipe, recipe_model)
        result = cls()
        result.__recipe = recipe
        result.name = recipe.name
        return result

    @classmethod
    def __create(cls, nomenclature, recipe, gross_weight_grams, net_weight_grams):
        """Проверить весовые значения и собрать строку состава рецепта."""
        gross = cls.__weight(gross_weight_grams)
        net = cls.__weight(net_weight_grams)
        if gross <= 0 or net <= 0 or net > gross:
            raise argument_exception("Вес нетто должен быть положительным и не превышать вес брутто")

        result = cls()
        result.__nomenclature = nomenclature
        result.__recipe = recipe
        result.__gross_weight_grams = gross
        result.__net_weight_grams = net
        result.name = nomenclature.name if nomenclature is not None else recipe.name
        return result

    @staticmethod
    def __weight(value) -> Decimal:
        """Преобразовать числовой вес в Decimal или сообщить об ошибке."""
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise argument_exception("Вес ингредиента должен быть числом в граммах")
        try:
            return Decimal(str(value))
        except InvalidOperation as error:
            raise argument_exception("Вес ингредиента должен быть числом в граммах") from error
