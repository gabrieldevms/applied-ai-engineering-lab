from ai_api.multi_agent.schemas import MultiAgentRoleDescriptor


def build_default_multi_agent_roles() -> list[MultiAgentRoleDescriptor]:
    return [
        MultiAgentRoleDescriptor(
            name="orchestrator_agent",
            title="Orchestrator Agent",
            responsibility=(
                "Coordinate the multi-agent QA workflow and define the execution plan."
            ),
            inputs=[
                "requirement_text",
                "objective",
                "context",
            ],
            outputs=[
                "workflow_plan",
            ],
        ),
        MultiAgentRoleDescriptor(
            name="requirement_analyst_agent",
            title="Requirement Analyst Agent",
            responsibility=(
                "Understand the requirement and identify business rules, open "
                "questions and testing implications."
            ),
            inputs=[
                "requirement_text",
                "workflow_plan",
            ],
            outputs=[
                "requirement_analysis",
            ],
        ),
        MultiAgentRoleDescriptor(
            name="functional_qa_agent",
            title="Functional QA Agent",
            responsibility=(
                "Identify functional test coverage, positive scenarios, negative "
                "scenarios and edge cases."
            ),
            inputs=[
                "requirement_analysis",
                "context",
            ],
            outputs=[
                "functional_test_strategy",
            ],
        ),
        MultiAgentRoleDescriptor(
            name="test_automation_agent",
            title="Test Automation Agent",
            responsibility=(
                "Propose automation candidates, test layers and implementation notes."
            ),
            inputs=[
                "functional_test_strategy",
                "context",
            ],
            outputs=[
                "test_automation_strategy",
            ],
        ),
        MultiAgentRoleDescriptor(
            name="reviewer_agent",
            title="Reviewer Agent",
            responsibility=(
                "Review the multi-agent outputs and identify gaps, risks and "
                "consistency issues."
            ),
            inputs=[
                "requirement_analysis",
                "functional_test_strategy",
                "test_automation_strategy",
            ],
            outputs=[
                "review_findings",
            ],
        ),
        MultiAgentRoleDescriptor(
            name="report_agent",
            title="Report Agent",
            responsibility=(
                "Generate the final QA report from the shared multi-agent state."
            ),
            inputs=[
                "review_findings",
                "shared_state",
            ],
            outputs=[
                "final_qa_report",
            ],
        ),
    ]
