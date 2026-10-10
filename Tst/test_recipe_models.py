from decimal import Decimal

import pytest

from Src.Core.validator import argument_exception
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_ingredient_model import recipe_ingredient_model
from Src.Models.recipe_model import recipe_model
from Src.Models.settings_model import settings_model


def test_create_borsch_recipe_with_semi_finished_recipe():
    recipe = recipe_model.create_borsch()

    assert recipe.name == "Борщ столичный"
    assert recipe.portions == 10
    assert len(recipe.ingredients) == 12
    assert len(recipe.steps) == 4
    assert recipe.ingredients[0].recipe.name == "Пассеровка свекольная"


def test_borsch_gross_and_net_weights_include_semi_finished_recipe():
    recipe = recipe_model.create_borsch()

    assert recipe.gross_weight_grams == Decimal("7273")
    assert recipe.net_weight_grams == Decimal("6790")
    assert recipe.ingredients[0].recipe.gross_weight_grams == Decimal("1092")
    assert recipe.ingredients[0].recipe.net_weight_grams == Decimal("1012")
    assert {item.nomenclature.group.name for item in recipe.ingredients
            if item.nomenclature is not None} == {
                "Овощи", "Мясные продукты", "Вспомогательные продукты",
                "Бакалея", "Молочные продукты"}


def test_recipe_weights_are_recalculated_when_ingredient_is_added_and_removed():
    recipe = recipe_model.create_borsch()
    group = recipe.ingredients[1].nomenclature.group
    unit = range_model.create_gram()
    ingredient = nomenclature_model.create_ingredient("Дополнительная вода", group, unit)
    line = recipe_ingredient_model.create_for_nomenclature(ingredient, 100, 80)

    recipe.add_ingredient(line)
    assert recipe.gross_weight_grams == Decimal("7373")
    assert recipe.net_weight_grams == Decimal("6870")

    recipe.remove_ingredient(line)
    assert recipe.gross_weight_grams == Decimal("7273")
    assert recipe.net_weight_grams == Decimal("6790")


def test_parent_weight_tracks_changes_to_semi_finished_recipe():
    recipe = recipe_model.create_borsch()
    saute = recipe.ingredients[0].recipe
    group = saute.ingredients[0].nomenclature.group
    unit = range_model.create_gram()
    ingredient = nomenclature_model.create_ingredient("Дополнительная свёкла", group, unit)
    line = recipe_ingredient_model.create_for_nomenclature(ingredient, 10, 8)

    saute.add_ingredient(line)
    assert recipe.gross_weight_grams == Decimal("7283")
    assert recipe.net_weight_grams == Decimal("6798")

    saute.remove_ingredient(line)
    assert recipe.gross_weight_grams == Decimal("7273")
    assert recipe.net_weight_grams == Decimal("6790")


def test_recipe_rejects_net_weight_greater_than_gross_weight():
    recipe = recipe_model.create_borsch()
    first_line = recipe.ingredients[1]
    ingredient = nomenclature_model.create_ingredient(
        "Некорректный ингредиент",
        first_line.nomenclature.group,
        first_line.nomenclature.range)

    with pytest.raises(argument_exception):
        recipe_ingredient_model.create_for_nomenclature(ingredient, 10, 11)


def test_first_start_seeds_borsch_recipe_and_its_nomenclature():
    manager = storage_manager(settings_model())

    assert manager.build() is True
    recipes = manager.data[storage_manager.recipe_key()]
    assert len(recipes) == 1
    assert recipes[0].name == "Борщ столичный"
    assert any(item.name == "Свёкла" for item in manager.data[storage_manager.nomenclature_key()])
    assert len(manager.data[storage_manager.range_key()]) == 3
    assert manager.build() is False
    assert manager.data[storage_manager.recipe_key()] == recipes


def test_recipe_rejects_circular_semi_finished_recipe():
    first = recipe_model()
    first.name = "Первый"
    first.portions = 1
    group = recipe_model.create_borsch().ingredients[1].nomenclature.group
    unit = range_model.create_gram()
    ingredient = nomenclature_model.create_ingredient("Ингредиент", group, unit)
    first.add_ingredient(recipe_ingredient_model.create_for_nomenclature(ingredient, 1, 1))
    second = recipe_model()
    second.name = "Второй"
    second.portions = 1
    second.add_ingredient(recipe_ingredient_model.create_for_recipe(first))

    with pytest.raises(argument_exception):
        first.add_ingredient(recipe_ingredient_model.create_for_recipe(second))
