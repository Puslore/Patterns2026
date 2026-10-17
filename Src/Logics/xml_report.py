from xml.etree.ElementTree import Element, SubElement, tostring

from Src.Core.abstract_report import abstract_report


class xml_report(abstract_report):
    """Форматировать отчет как XML-документ."""

    content_type = "application/xml; charset=utf-8"

    def format_data(self, data: dict) -> str:
        root = Element("report")
        self._append_value(root, "entity", data)
        return tostring(root, encoding="unicode", xml_declaration=False)

    @classmethod
    def _append_value(cls, parent, name, value):
        node = SubElement(parent, name)
        if isinstance(value, dict):
            for key, item in value.items():
                cls._append_value(node, key, item)
        elif isinstance(value, list):
            for item in value:
                cls._append_value(node, "item", item)
        elif value is not None:
            node.text = str(value)
