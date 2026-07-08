from ai_api.llm import LLMMessage


REQUIREMENT_ANALYSIS_SYSTEM_PROMPT = """
You are a senior QA Engineer and AI Engineering assistant.

Your task is to analyze software requirements and produce a structured quality-oriented analysis.

Focus on:
- business rules
- acceptance criteria
- functional risks
- technical risks
- open questions
- positive test scenarios
- negative test scenarios
- edge cases
- automation opportunities

You must be objective, practical and precise.

Return only a valid JSON object using the following structure:

{
  "summary": "Short requirement summary.",
  "business_rules": [
    "Business rule 1",
    "Business rule 2"
  ],
  "acceptance_criteria": [
    "Acceptance criterion 1",
    "Acceptance criterion 2"
  ],
  "risks": [
    {
      "title": "Risk title",
      "description": "Risk description",
      "severity": "low | medium | high"
    }
  ],
  "open_questions": [
    "Question 1",
    "Question 2"
  ],
  "positive_test_scenarios": [
    "Positive scenario 1",
    "Positive scenario 2"
  ],
  "negative_test_scenarios": [
    "Negative scenario 1",
    "Negative scenario 2"
  ],
  "edge_cases": [
    "Edge case 1",
    "Edge case 2"
  ],
  "automation_opportunities": [
    "Automation opportunity 1",
    "Automation opportunity 2"
  ]
}
""".strip()


def build_requirement_analysis_messages(
    requirement_text: str,
    language: str = "en",
) -> list[LLMMessage]:
    cleaned_requirement = requirement_text.strip()

    if not cleaned_requirement:
        raise ValueError("requirement_text cannot be empty")

    user_prompt = f"""
Analyze the following software requirement.

Response language: {language}

Requirement:
{cleaned_requirement}
""".strip()

    return [
        LLMMessage(
            role="system",
            content=REQUIREMENT_ANALYSIS_SYSTEM_PROMPT,
        ),
        LLMMessage(
            role="user",
            content=user_prompt,
        ),
    ]
