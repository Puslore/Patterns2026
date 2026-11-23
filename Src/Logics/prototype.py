from Src.Core.abstract_prototype import abstract_prototype
from Src.Dtos.filter_dto import filter_dto

class prototype (abstract_prototype):

    def clone(self, filter: filter_dto) -> "prototype":

        # Фильтрация
        #for item in filter:
        #    # ....
        #    self.__data = []


        result = prototype( self.__data )
        return result


    
