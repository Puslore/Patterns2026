from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.abstract_model import abstact_model
from Src.Core.common import common

"""
Реализация TXT представления отчета по рецепту
"""
class text_report(abstract_report):

    """
    Переопределенный метод формирования отчета
    """
    def build(self, source: abstact_model) -> report_result_dto:
        validator.validate(source, abstact_model)
        lines = [] 

        # Заголовок
        headers = common.get_entity_header(source) 
        lines.append("Заголовок") 
        for header in headers: 
            lines.append(f"{header.field}: {header.value}") 
            lines.append("") 
            
        # Табличная часть
        table_data = common.get_entity_table(source) 
        if table_data and len(table_data[0].columns) > 1: 
            # Это агрегат со списком 
            lines.append("Табличная часть") 
            table = table_data[0] 
            # Формируем строку заголовков 
            header_line = " | ".join([col.replace('_', ' ').capitalize() for col in table.columns]) 
            lines.append(header_line) 
            lines.append("-" * len(header_line)) 
            
            # Формируем строку значений 
            values_line = " | ".join(table.values) 
            lines.append(values_line) 
            
        result = report_result_dto()
        result.text = "\n".join(lines) 
        result.format = "text/plain"

        return result


