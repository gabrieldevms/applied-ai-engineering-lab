import type { AppPage } from "../types/navigation";

type ProductPlaceholderPageProps = {
  page: AppPage;
};

const pageContent: Record<
  AppPage,
  {
    eyebrow: string;
    title: string;
    description: string;
    plannedItems: string[];
  }
> = {
  overview: {
    eyebrow: "Command Center",
    title: "Overview",
    description: "Visão geral do AI Quality Command Center.",
    plannedItems: [],
  },
  observability: {
    eyebrow: "Observability",
    title: "Observability Center",
    description: "Área de observabilidade de sistemas de IA.",
    plannedItems: [],
  },
    "execution-history": {
    eyebrow: "Execution History",
    title: "Histórico de Execuções",
    description:
      "Linha do tempo operacional consolidada a partir das telemetrias persistidas de avaliação, usage, RAG, agentes e execução multiagente.",
    plannedItems: [],
  },
    "usage-cost": {
    eyebrow: "LLMOps",
    title: "Usage & Cost",
    description:
      "Visualização de tokens, custos estimados, coverage por provider/modelo e riscos de usage tracking.",
    plannedItems: [],
  },
    "risk-center": {
    eyebrow: "Risk Center",
    title: "Central de Riscos",
    description:
      "Painéis consolidados de riscos, recomendações e sinais de atenção da plataforma.",
    plannedItems: [],
  },
  evaluation: {
    eyebrow: "Evaluation",
    title: "Evaluation Center",
    description:
      "Área futura para visualizar suites, cenários, quality gates e resultados de avaliação.",
    plannedItems: [
      "Golden Dataset",
      "Prompt Regression",
      "LLM Output Evaluation",
      "RAG Regression",
      "Agent Regression",
      "Tool-calling Evaluation",
      "LLM-as-judge",
      "AI Evaluation Pipeline",
    ],
  },
  "qa-agent": {
    eyebrow: "Agent Console",
    title: "QA Agent Console",
    description:
      "Área futura para executar e revisar análises do QA Agent com rastreabilidade.",
    plannedItems: [
      "Execução do QA Agent",
      "Análise de requisitos",
      "Evidências de dados",
      "Trace de execução",
      "Quality checks",
    ],
  },
  "multi-agent-copilot": {
    eyebrow: "Multi-Agent",
    title: "Multi-Agent Copilot Console",
    description:
      "Área futura para executar o fluxo multiagente e revisar artefatos, contratos e relatório final.",
    plannedItems: [
      "Orchestrator Agent",
      "Functional QA Agent",
      "Test Automation Agent",
      "Reviewer Agent",
      "Report Agent",
      "Final QA Report",
    ],
  },
  rag: {
    eyebrow: "RAG",
    title: "RAG Console",
    description:
      "Área futura para ingestão, recuperação, respostas fundamentadas e análise de qualidade do RAG.",
    plannedItems: [
      "Ingestão de documentos",
      "Extração de texto",
      "Busca semântica",
      "Context retrieval",
      "Respostas com citações",
      "Métricas de retrieval",
    ],
  },
  "data-analyst": {
    eyebrow: "Data",
    title: "Data Analyst Console",
    description:
      "Área futura para validações com dados, geração SQL segura e evidências de consulta.",
    plannedItems: [
      "Schema explorer",
      "Pergunta em linguagem natural",
      "SQL gerado",
      "Validação read-only",
      "Resultado da consulta",
      "Evidências",
    ],
  },
  "provider-settings": {
    eyebrow: "Settings",
    title: "Configurações de provider",
    description:
      "Área futura para visualizar configurações de providers, modelos e estratégias de execução.",
    plannedItems: [
      "Provider ativo",
      "Modelos configurados",
      "Health check",
      "Fallback strategy",
      "Timeouts",
      "Custos estimados",
    ],
  },
};

export function ProductPlaceholderPage({ page }: ProductPlaceholderPageProps) {
  const content = pageContent[page];

  return (
    <div className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">{content.eyebrow}</span>
          <h1>{content.title}</h1>
          <p>{content.description}</p>
        </div>
      </section>

      <section className="placeholder-card">
        <h2>Planejado para o M8</h2>
        <p>
          Esta área já está reservada na arquitetura do frontend e será expandida
          em próximos PRs.
        </p>

        {content.plannedItems.length > 0 ? (
          <ul className="planned-list">
            {content.plannedItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : null}
      </section>
    </div>
  );
}
