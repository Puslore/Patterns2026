from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.abstract_model import abstact_model
from Src.Core.common import common
from Src.Core.abstract_model import abstact_model
from Src.Core.entity_model import entity_model


"""
Реализация CSV представления отчета по рецепту
"""
class csv_report(abstract_report):

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source: abstact_model) -> report_result_dto:
        validator.validate(source, abstact_model)
        lines = [] 
    
        headers = common.get_entity_header(source) 
        # Заголовок
        header_line = " ; ".join([header.field.capitalize() for header in headers]) 
        # Данные
        data_line = " ; ".join([ str(header.value) for header in headers]) 

        lines.append(header_line)
        lines.append(data_line)
              
        result = report_result_dto()
        result.text = "\n".join(lines) 
        result.format = "text/plain"
    
        return result