# UML моделей технологических карт

```mermaid
classDiagram
    direction TB

    class entity_model {
        +name: str
        +unique_code: str
    }

    class nomenclature_model {
        +group: group_model
        +range: range_model
        +create_ingredient(name, group, unit)$
    }

    class group_model {
        +create(name)$
        +create_ingredients()$
    }

    class range_model {
        +create_gram()$
        +create_piece()$
        +create_milliliter()$
    }

    class recipe_model {
        +category: str
        +portions: int
        +ingredients: list
        +steps: list
        +gross_weight_grams: Decimal
        +net_weight_grams: Decimal
        +add_ingredient(ingredient)
        +remove_ingredient(ingredient)
        +add_step(step)
        +create_borsch()$
    }

    class recipe_ingredient_model {
        +name: str
        +nomenclature: nomenclature_model
        +recipe: recipe_model
        +gross_weight_grams: Decimal
        +net_weight_grams: Decimal
        +create_for_nomenclature(item, gross, net)$
        +create_for_recipe(recipe)$
    }

    class recipe_step_model {
        +number: int
        +instructions: str
        +duration_minutes: int
        +create(number, title, instructions, duration)$
    }

    entity_model <|-- nomenclature_model
    entity_model <|-- group_model
    entity_model <|-- range_model
    entity_model <|-- recipe_model
    entity_model <|-- recipe_ingredient_model
    entity_model <|-- recipe_step_model
    nomenclature_model --> group_model
    nomenclature_model --> range_model
    recipe_model *-- "1..*" recipe_ingredient_model : состав
    recipe_model *-- "0..*" recipe_step_model : этапы
    recipe_ingredient_model --> "0..1" nomenclature_model : продукт
    recipe_ingredient_model --> "0..1" recipe_model : полуфабрикат
```

Каждая строка состава ссылается ровно на продукт или на вложенную технологическую
карту полуфабриката. Вес рецепта рекурсивно суммирует массу брутто и нетто строк;
значения хранятся в граммах. Добавление вложенной карты запрещает циклические
зависимости.
