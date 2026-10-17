import json

from Src.Core.abstract_report import abstract_report


class text_report(abstract_report):
    """Текстовый отчет в структурированном JSON-представлении."""

    content_type = "text/plain; charset=utf-8"

    def format_data(self, data: dict) -> str:
        return json.dumps(data, ensure_ascii=False, indent=2)
