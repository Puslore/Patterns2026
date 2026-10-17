import csv
from io import StringIO

from Src.Core.abstract_report import abstract_report
from Src.Logics.report_data import flatten_report_data


class csv_report(abstract_report):
    """Сформировать CSV-файл с путем и значением каждого поля отчета."""

    content_type = "text/csv; charset=utf-8"
    filename = "report.csv"

    def format_data(self, data: dict) -> bytes:
        output = StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(("Поле", "Значение"))
        writer.writerows(flatten_report_data(data))
        return output.getvalue().encode("utf-8")
