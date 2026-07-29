from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


QADataValidationDecision = Literal[
    "selected",
    "skipped",
]


class QADataValidationSelectionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: QADataValidationDecision
    reason: str
    matched_signals: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class QADataValidationSelector:
    def __init__(
        self,
        minimum_signal_count: int = 2,
    ) -> None:
        self.minimum_signal_count = minimum_signal_count
        self._signals = [
            "saldo",
            "conta",
            "contas",
            "depósito",
            "deposito",
            "depósitos",
            "depositos",
            "retirada",
            "retiradas",
            "saque",
            "saques",
            "transação",
            "transacao",
            "transações",
            "transacoes",
            "pagamento",
            "pagamentos",
            "boleto",
            "boletos",
            "valor",
            "valores",
            "cálculo",
            "calculo",
            "calcular",
            "validar dados",
            "base de dados",
            "banco de dados",
            "tabela",
            "tabelas",
            "registro",
            "registros",
            "consulta",
            "sql",
            "relatório",
            "relatorio",
            "cnab",
            "financeiro",
            "renegociação",
            "renegociacao",
            "quitação",
            "quitacao",
        ]

    def select(
        self,
        requirement_text: str,
    ) -> QADataValidationSelectionResult:
        normalized_text = self._normalize(requirement_text)

        matched_signals = [
            signal
            for signal in self._signals
            if signal in normalized_text
        ]

        unique_matched_signals = sorted(set(matched_signals))

        if len(unique_matched_signals) >= self.minimum_signal_count:
            return QADataValidationSelectionResult(
                decision="selected",
                reason=(
                    "Data validation was selected because the requirement "
                    "contains data-related validation signals."
                ),
                matched_signals=unique_matched_signals,
                confidence=min(
                    1.0,
                    len(unique_matched_signals) / 6,
                ),
            )

        return QADataValidationSelectionResult(
            decision="skipped",
            reason=(
                "Data validation was skipped because the requirement did not "
                "contain enough data-related validation signals."
            ),
            matched_signals=unique_matched_signals,
            confidence=min(
                0.5,
                len(unique_matched_signals) / 6,
            ),
        )

    def _normalize(
        self,
        value: str,
    ) -> str:
        return value.strip().lower()
