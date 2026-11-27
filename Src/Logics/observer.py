from Src.Core.abstract_observabile import abstract_observabile
from Src.Core.validator import validator

"""
Реализация диспетчера шаблона Наблюдатель (Observer)
"""
class observer:
    # Список наблюдателей
    handlers: list[abstract_observabile] = []


    """
    Добавить под наблюдение
    """    
    @staticmethod
    def add( sourse: abstract_observabile ) -> None:
        validator.validate( sourse, abstract_observabile)
        
        for handler in observer.handlers:
            if handler == sourse:
                return

        observer.handlers.append( sourse )

    """
    Удалить из под наблюдения
    """
    @staticmethod
    def delete( sourse: abstract_observabile ) -> None:
        validator.validate( sourse, abstract_observabile)
                
        for handler in observer.handlers:
            if handler == sourse:
                observer.handlers.remove ( handler )


    """
    Вызвать сообщение
    """
    @staticmethod
    def create( event_types:str, params:object = None ) -> None:
        for handler in observer.handlers:
            if handler is not None:
                handler.handler( event_types, params )


