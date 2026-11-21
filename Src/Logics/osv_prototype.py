from typing import List

from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.osv_item_dto import osv_item_dto
from Src.Logics.prototype import prototype
from Src.Models.transaction_model import transaction_model


class osv_prototype(prototype):
    """
    Прототип формирования оборотно-сальдовой ведомости.

    Наследует универсальную фильтрацию складских транзакций и после
    клонирования преобразует отфильтрованный набор в строки ОСВ.
    """

    def clone(self, filter: filter_dto = None) -> "osv_prototype":
        """
        Склонировать прототип, отфильтровать транзакции и сформировать строки ОСВ.
        """
        filtered = super().clone(filter)
        return osv_prototype(self._build_rows(filtered.data))

    def _build_rows(self, transactions: list) -> List[osv_item_dto]:
        """
        Сгруппировать транзакции по складу, номенклатуре и единице измерения.
        """
        groups = {}
        for transaction in transactions:
            if not isinstance(transaction, transaction_model):
                continue
            if transaction.storage is None or transaction.nomenclature is None:
                continue

            range_code = transaction.range.unique_code if transaction.range else ""
            key = (
                transaction.storage.unique_code,
                transaction.nomenclature.unique_code,
                range_code,
            )
            groups.setdefault(key, []).append(transaction)

        rows: List[osv_item_dto] = []
        for group in groups.values():
            rows.append(self._create_row(group))

        rows.sort(key=lambda row: row.nomenclature_name)
        return rows

    def _create_row(self, transactions: list) -> osv_item_dto:
        """
        Рассчитать начальный остаток, обороты и конечный остаток по группе транзакций.
        """
        first = transactions[0]
        turnover_in = sum(item.value for item in transactions if item.value > 0)
        turnover_out = sum(abs(item.value) for item in transactions if item.value < 0)
        initial_balance = 0.0

        row = osv_item_dto()
        row.storage_name = first.storage.name
        row.storage_code = first.storage.unique_code
        row.nomenclature_name = first.nomenclature.name
        row.nomenclature_code = first.nomenclature.unique_code
        if first.range is not None:
            row.range_name = first.range.name
            row.range_code = first.range.unique_code
        row.initial_balance = initial_balance
        row.turnover_in = turnover_in
        row.turnover_out = turnover_out
        row.final_balance = initial_balance + turnover_in - turnover_out
        return row
