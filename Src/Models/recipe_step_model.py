from Src.Core.entity_model import entity_model
from Src.Core.validator import argument_exception, validator


class recipe_step_model(entity_model):
    __number: int = 0
    __instructions: str = ""
    __duration_minutes: int = 0

    @property
    def number(self) -> int:
        return self.__number

    @property
    def instructions(self) -> str:
        return self.__instructions

    @property
    def duration_minutes(self) -> int:
        return self.__duration_minutes

    @staticmethod
    def create(number: int, title: str, instructions: str, duration_minutes: int = 0):
        validator.validate(number, int)
        validator.validate(title, str)
        validator.validate(instructions, str)
        validator.validate(duration_minutes, int)
        if number <= 0 or duration_minutes < 0:
            raise argument_exception("Некорректный номер или длительность этапа")

        result = recipe_step_model()
        result.name = title
        result.__number = number
        result.__instructions = instructions.strip()
        result.__duration_minutes = duration_minutes
        return result
