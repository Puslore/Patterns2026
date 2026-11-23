from Src.Core.abstract_model import abstact_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
import datetime
from Src.Core.validator import argument_exception

"""
Модель транзакции
"""
class transaction_model(abstact_model):
    __range:range_model = None
    __storage:storage_model = None
    __nomenclature:nomenclature_model = None
    __value:float # + поступление, - списание
    __period: datetime.datetime


    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, source:float) -> None:
        if source == 0:
            raise argument_exception("Значение = 0 !")
        self.__value = source

