from typing import Dict, List, Tuple

from Src.Core.filter_type_enum import filter_type_enum
from Src.Core.validator import argument_exception, operation_exception, validator
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Dtos.osv_item_dto import osv_item_dto
from Src.Logics.convertor import convertor
from Src.Logics.prototype import prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.transaction_model import transaction_model


class osv_service:
    """
    Сервис формирования оборотно-сальдовой ведомости.

    Получает транзакции из менеджера хранилища, применяет к ним фильтры
    через шаблон Прототип, рассчитывает начальные остатки, обороты и
    конечные остатки, после чего сериализует строки отчета.
    """

    # Менеджер доменных данных
    __storage: storage_manager = None
    # Конвертор для сериализации результата
    __convertor: convertor = None

    def __init__(self, storage: storage_manager):
        """
        Инициализировать сервис формирования ОСВ.
        """
        validator.validate(storage, storage_manager)
        self.__storage = storage
        self.__convertor = convertor()

    def build(self, filter_data: object = None) -> List[dict]:
        """
        Сформировать и сериализовать строки оборотно-сальдовой ведомости.
        """
        rows = self.build_items(filter_data)
        return [self._serialize(row) for row in rows]

    def build_items(self, filter_data: object = None) -> List[osv_item_dto]:
        """
        Сформировать строки оборотно-сальдовой ведомости как DTO.
        """
        dto = self._to_filter_dto(filter_data)
        start_date = dto.start_date
        end_date = dto.end_date

        if start_date is not None and end_date is not None and start_date > end_date:
            raise argument_exception(
                "Дата начала периода не может быть позже даты окончания!"
            )

        # Начальные остатки: транзакции с датой не позже начала периода
        initial_transactions = self._filter_initial(dto, start_date)
        # Обороты: транзакции внутри периода (после начала и по окончание)
        turnover_transactions = self._filter_turnover(dto, start_date, end_date)
        # Объединение записей и расчет конечных остатков
        return self._merge_rows(initial_transactions, turnover_transactions)

    def _to_filter_dto(self, filter_data: object) -> filter_dto:
        """
        Десериализовать параметры фильтрации в DTO.
        """
        if filter_data is None:
            return filter_dto()

        if isinstance(filter_data, filter_dto):
            return filter_data

        if isinstance(filter_data, dict):
            return filter_dto().from_dict(filter_data)

        raise argument_exception("Тело запроса должно быть JSON-объектом!")

    def _filter_initial(
        self,
        dto: filter_dto,
        start_date,
    ) -> List[transaction_model]:
        """
        Получить транзакции для расчета начальных остатков (дата <= начала).
        """
        if start_date is None:
            return []

        criteria = self._base_criteria(dto)
        criteria.append(
            filter_item_dto("period", filter_type_enum.LESS_EQUAL, start_date)
        )
        return self._apply_filter(criteria)

    def _filter_turnover(
        self,
        dto: filter_dto,
        start_date,
        end_date,
    ) -> List[transaction_model]:
        """
        Получить транзакции для расчета оборотов (даты ОТ и ДО).
        """
        criteria = self._base_criteria(dto)

        if start_date is not None:
            # Начальная дата уже вошла в начальный остаток, поэтому
            # обороты начинаются строго после нее.
            criteria.append(
                filter_item_dto("period", filter_type_enum.GREATER, start_date)
            )

        if end_date is not None:
            criteria.append(
                filter_item_dto("period", filter_type_enum.LESS_EQUAL, end_date)
            )

        return self._apply_filter(criteria)

    @staticmethod
    def _base_criteria(dto: filter_dto) -> List[filter_item_dto]:
        """
        Получить критерии фильтрации доменных полей без периода.
        """
        return list(dto.filters)

    def _apply_filter(self, criteria: List[filter_item_dto]) -> List[transaction_model]:
        """
        Применить критерии к актуальным данным менеджера через Прототип.
        """
        transactions = self._get_transactions()
        if not criteria:
            return transactions

        flt = filter_dto()
        flt.filters = criteria
        return prototype(transactions).clone(flt).data

    def _get_transactions(self) -> List[transaction_model]:
        """
        Получить исходные транзакции из менеджера хранилища.
        """
        return list(
            self.__storage.data.get(storage_manager.transaction_key(), [])
        )

    def _merge_rows(
        self,
        initial_transactions: List[transaction_model],
        turnover_transactions: List[transaction_model],
    ) -> List[osv_item_dto]:
        """
        Объединить остатки и обороты по складу, номенклатуре и единице измерения.
        """
        initial_groups = self._group_transactions(initial_transactions)
        turnover_groups = self._group_transactions(turnover_transactions)

        keys = list(initial_groups.keys())
        for key in turnover_groups.keys():
            if key not in initial_groups:
                keys.append(key)

        rows: List[osv_item_dto] = []
        for key in keys:
            rows.append(
                self._create_row(
                    initial_groups.get(key, []),
                    turnover_groups.get(key, []),
                )
            )

        rows.sort(
            key=lambda row: (
                row.storage_name,
                row.nomenclature_name,
                row.range_name,
            )
        )
        return rows

    def _group_transactions(
        self,
        transactions: List[transaction_model],
    ) -> Dict[Tuple[str, str, str], List[transaction_model]]:
        """
        Сгруппировать транзакции по складу, номенклатуре и единице измерения.
        """
        groups: Dict[Tuple[str, str, str], List[transaction_model]] = {}

        for transaction in transactions:
            if not isinstance(transaction, transaction_model):
                continue
            if transaction.storage is None or transaction.nomenclature is None:
                continue

            range_code = (
                transaction.range.unique_code
                if transaction.range is not None
                else ""
            )
            key = (
                transaction.storage.unique_code,
                transaction.nomenclature.unique_code,
                range_code,
            )
            groups.setdefault(key, []).append(transaction)

        return groups

    def _create_row(
        self,
        initial_transactions: List[transaction_model],
        turnover_transactions: List[transaction_model],
    ) -> osv_item_dto:
        """
        Рассчитать начальный остаток, обороты и конечный остаток по группе.
        """
        first = (
            initial_transactions[0]
            if initial_transactions
            else turnover_transactions[0]
        )

        row = osv_item_dto()
        row.storage_name = first.storage.name
        row.storage_code = first.storage.unique_code
        row.nomenclature_name = first.nomenclature.name
        row.nomenclature_code = first.nomenclature.unique_code

        if first.range is not None:
            row.range_name = first.range.name
            row.range_code = first.range.unique_code

        row.initial_balance = sum(
            item.value for item in initial_transactions
        )
        row.turnover_in = sum(
            item.value for item in turnover_transactions if item.value > 0
        )
        row.turnover_out = sum(
            abs(item.value) for item in turnover_transactions if item.value < 0
        )
        row.final_balance = (
            row.initial_balance + row.turnover_in - row.turnover_out
        )
        return row

    def _serialize(self, row: osv_item_dto) -> dict:
        """
        Сериализовать строку ОСВ в словарь через общий конвертор.
        """
        result = self.__convertor.serialize(row)
        if self.__convertor.is_error or not isinstance(result, dict):
            raise operation_exception(
                self.__convertor.error_text or "Ошибка сериализации строки ОСВ"
            )

        return result.get("result", result)
