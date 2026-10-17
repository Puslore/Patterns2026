import html
import json

from Src.Core.abstract_report import abstract_report


class html_report(abstract_report):
    """Форматировать отчет как HTML-документ."""

    content_type = "text/html; charset=utf-8"

    def format_data(self, data: dict) -> str:
        title = html.escape(str(data.get("name", "Отчет")))
        body = html.escape(json.dumps(data, ensure_ascii=False, indent=2))
        return (
            "<!doctype html><html lang=\"ru\"><head>"
            "<meta charset=\"utf-8\"><title>"
            f"{title}</title></head><body><h1>{title}</h1>"
            f"<pre>{body}</pre></body></html>"
        )
