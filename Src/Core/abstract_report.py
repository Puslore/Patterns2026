from abc import ABC, abstractmethod
from dataclasses import dataclass

from Src.Core.abstract_model import abstact_model
from Src.Core.validator import argument_exception
from Src.Logics.report_data import to_report_data


@dataclass(frozen=True)
class report_result:
    content: bytes | str
    content_type: str
    filename: str | None = None


class abstract_report(ABC):
    content_type = "text/plain; charset=utf-8"
    filename = None

    def build(self, model: abstact_model) -> report_result:
        """Преобразовать модель в результат, пригодный для HTTP-ответа."""
        if not isinstance(model, abstact_model):
            raise argument_exception("Для формирования отчета требуется модель")
        data = to_report_data(model)
        content = self.format_data(data)
        if isinstance(content, str) and self.filename is not None:
            content = content.encode("utf-8")
        return report_result(content, self.content_type, self.filename)

    @abstractmethod
    def format_data(self, data: dict) -> bytes | str:
        """Сформировать представление данных в формате отчета."""
