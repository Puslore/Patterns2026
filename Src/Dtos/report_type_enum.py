from enum import Enum

"""
Типы отчетов
"""
class report_type_enum(Enum):
    
    """
    Текстовый формат
    """
    TXT = 1

    """
    Формат CSV
    """
    CSV = 2

    """
    Формат документации
    """
    MARKDOWN = 3
