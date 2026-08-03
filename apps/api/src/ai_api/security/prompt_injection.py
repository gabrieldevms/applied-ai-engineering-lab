from dataclasses import dataclass
from typing import Literal
from ai_api.security.schemas import (
    PromptInjectionAssessmentRequest,
    PromptInjectionAssessmentResponse,
    PromptInjectionRecommendedAction,
    PromptInjectionRiskLevel,
)


RuleRiskLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class PromptInjectionRule:
    pattern_id: str
    risk_level: RuleRiskLevel
    reason: str
    phrases: tuple[str, ...]


_RISK_ORDER: dict[PromptInjectionRiskLevel, int] = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}


_HIGH_RISK_RULES: tuple[PromptInjectionRule, ...] = (
    PromptInjectionRule(
        pattern_id="secret_exfiltration_attempt",
        risk_level="high",
        reason="Input appears to request secrets, tokens or credentials.",
        phrases=(
            "reveal secrets",
            "show secrets",
            "show api key",
            "reveal api key",
            "print api key",
            "show token",
            "reveal token",
            "print token",
            "show bearer token",
            "authorization header",
            "mostre a chave",
            "mostre a api key",
            "revele a chave",
            "revele segredos",
        ),
    ),
    PromptInjectionRule(
        pattern_id="system_prompt_extraction_attempt",
        risk_level="high",
        reason="Input appears to request hidden system or developer instructions.",
        phrases=(
            "show system prompt",
            "reveal system prompt",
            "print system prompt",
            "show developer instructions",
            "reveal developer instructions",
            "hidden instructions",
            "mostre o prompt do sistema",
            "revele o prompt do sistema",
            "instruções ocultas",
        ),
    ),
    PromptInjectionRule(
        pattern_id="validation_bypass_attempt",
        risk_level="high",
        reason="Input appears to request bypassing validation or safety controls.",
        phrases=(
            "bypass validation",
            "disable validation",
            "ignore validation",
            "do not validate",
            "skip validation",
            "burlar validação",
            "desabilite a validação",
            "ignore a validação",
            "não valide",
        ),
    ),
    PromptInjectionRule(
        pattern_id="destructive_data_operation_attempt",
        risk_level="high",
        reason="Input appears to request destructive data or SQL operations.",
        phrases=(
            "drop table",
            "truncate table",
            "delete all records",
            "update all records",
            "destroy data",
            "remove all data",
            "apague todos os registros",
            "exclua todos os registros",
            "remova todos os dados",
        ),
    ),
    PromptInjectionRule(
        pattern_id="data_exfiltration_attempt",
        risk_level="high",
        reason="Input appears to request data exfiltration.",
        phrases=(
            "exfiltrate",
            "leak data",
            "send all data to",
            "send data to",
            "extract all data",
            "exfiltrar",
            "vazar dados",
            "envie todos os dados",
        ),
    ),
)


_MEDIUM_RISK_RULES: tuple[PromptInjectionRule, ...] = (
    PromptInjectionRule(
        pattern_id="instruction_override_attempt",
        risk_level="medium",
        reason="Input appears to override prior instructions or rules.",
        phrases=(
            "ignore previous instructions",
            "ignore all above",
            "forget your rules",
            "do not follow the original task",
            "override previous instructions",
            "ignore as instruções anteriores",
            "ignore todas as instruções anteriores",
            "esqueça suas regras",
        ),
    ),
    PromptInjectionRule(
        pattern_id="role_manipulation_attempt",
        risk_level="medium",
        reason="Input appears to manipulate the model role or execution mode.",
        phrases=(
            "you are now",
            "developer mode",
            "jailbreak",
            "act as an unrestricted",
            "aja como",
            "modo desenvolvedor",
        ),
    ),
    PromptInjectionRule(
        pattern_id="unauthorized_tool_request",
        risk_level="medium",
        reason="Input appears to request direct tool or command execution.",
        phrases=(
            "call this tool",
            "use this tool",
            "execute this command",
            "run this command",
            "run shell",
            "chame esta ferramenta",
            "use esta ferramenta",
            "execute este comando",
            "rode este comando",
        ),
    ),
    PromptInjectionRule(
        pattern_id="encoded_instruction_attempt",
        risk_level="medium",
        reason="Input appears to hide or reframe instructions indirectly.",
        phrases=(
            "base64 decode this instruction",
            "decode this hidden instruction",
            "the real instruction is",
            "a instrução real é",
            "decodifique esta instrução",
        ),
    ),
)


_LOW_RISK_RULES: tuple[PromptInjectionRule, ...] = (
    PromptInjectionRule(
        pattern_id="security_topic_reference",
        risk_level="low",
        reason="Input references prompt-injection-related security topics.",
        phrases=(
            "prompt injection",
            "system prompt",
            "developer instructions",
            "api key",
            "token",
            "secret",
            "prompt injection",
            "prompt do sistema",
            "chave de api",
            "segredo",
        ),
    ),
)


_EDUCATIONAL_CONTEXT_PHRASES: tuple[str, ...] = (
    "study",
    "studying",
    "learn",
    "learning",
    "educational",
    "example",
    "documentation",
    "article",
    "how to detect",
    "how to prevent",
    "estudo",
    "estudar",
    "aprendendo",
    "aprender",
    "educacional",
    "exemplo",
    "documentação",
    "artigo",
    "como detectar",
    "como prevenir",
)


class PromptInjectionDetectionService:
    def assess(
        self,
        request: PromptInjectionAssessmentRequest,
    ) -> PromptInjectionAssessmentResponse:
        normalized_text = _normalize_text(request.text)

        detected_rules = _detect_rules(normalized_text)
        risk_level = _resolve_risk_level(
            detected_rules=detected_rules,
            normalized_text=normalized_text,
        )
        recommended_action = _recommended_action_for(risk_level)

        return PromptInjectionAssessmentResponse(
            risk_level=risk_level,
            recommended_action=recommended_action,
            is_blocking_required=recommended_action == "block",
            detected_patterns=_unique_sorted(
                rule.pattern_id for rule in detected_rules
            ),
            risk_reasons=_unique_sorted(rule.reason for rule in detected_rules),
            input_source=request.input_source,
            workflow=request.workflow,
            inspected_character_count=len(request.text),
        )


def _detect_rules(normalized_text: str) -> list[PromptInjectionRule]:
    rules = [
        *_HIGH_RISK_RULES,
        *_MEDIUM_RISK_RULES,
        *_LOW_RISK_RULES,
    ]

    return [
        rule
        for rule in rules
        if any(phrase in normalized_text for phrase in rule.phrases)
    ]


def _resolve_risk_level(
    detected_rules: list[PromptInjectionRule],
    normalized_text: str,
) -> PromptInjectionRiskLevel:
    if not detected_rules:
        return "none"

    highest_risk = max(
        (rule.risk_level for rule in detected_rules),
        key=lambda level: _RISK_ORDER[level],
    )

    if highest_risk == "medium" and _has_educational_context(normalized_text):
        return "low"

    return highest_risk


def _recommended_action_for(
    risk_level: PromptInjectionRiskLevel,
) -> PromptInjectionRecommendedAction:
    if risk_level == "high":
        return "block"

    if risk_level == "medium":
        return "allow_with_warning"

    return "allow"


def _has_educational_context(normalized_text: str) -> bool:
    return any(phrase in normalized_text for phrase in _EDUCATIONAL_CONTEXT_PHRASES)


def _normalize_text(text: str) -> str:
    return " ".join(text.casefold().split())


def _unique_sorted(values: object) -> list[str]:
    return sorted(set(str(value) for value in values))
