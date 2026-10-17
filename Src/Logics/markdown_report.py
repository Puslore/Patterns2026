from Src.Core.abstract_report import abstract_report
from Src.Logics.report_data import flatten_report_data


class markdown_report(abstract_report):
    """Форматировать отчет как Markdown-таблицу для скачивания."""

    content_type = "text/markdown; charset=utf-8"
    filename = "report.md"

    def format_data(self, data: dict) -> str:
        title = data.get("name", "Отчет")
        lines = [
            f"# {title}",
            "",
            "| Поле | Значение |",
            "| --- | --- |",
        ]
        for path, value in flatten_report_data(data):
            escaped_path = path.replace("|", "\\|")
            escaped_value = value.replace("|", "\\|").replace("\n", "<br>")
            lines.append(f"| {escaped_path} | {escaped_value} |")
        return "\n".join(lines) + "\n"
