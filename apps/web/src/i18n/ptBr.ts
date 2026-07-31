import type { AppPage } from "../types/navigation";
import type { DashboardStatus } from "../types/observability";

export type NavigationItem = {
  page: AppPage;
  label: string;
};

export const navigationItems: NavigationItem[] = [
  {
    page: "overview",
    label: "Overview",
  },
  {
    page: "observability",
    label: "Central de Observabilidade",
  },
  {
    page: "usage-cost",
    label: "Uso e Custos",
  },
  {
    page: "evaluation",
    label: "Central de Avaliação",
  },
  {
    page: "qa-agent",
    label: "QA Agent",
  },
  {
    page: "multi-agent-copilot",
    label: "Multi-Agent Copilot",
  },
  {
    page: "rag",
    label: "RAG",
  },
  {
    page: "data-analyst",
    label: "Data Analyst",
  },
  {
    page: "provider-settings",
    label: "Configurações de provider",
  },
];

const statusLabels: Record<DashboardStatus, string> = {
  healthy: "Saudável",
  warning: "Atenção",
  critical: "Crítico",
  empty: "Sem dados",
};

const sectionTitleLabels: Record<string, string> = {
  evaluation_telemetry: "Telemetria de execução de IA",
  usage: "Uso de tokens e custos",
  retrieval_quality: "Qualidade de recuperação",
  agent_execution: "Execução de agentes",
  multi_agent_execution: "Execução multiagente",
};

const metricLabels: Record<string, string> = {
  record_count: "registros",
  event_count: "eventos",
  total_events: "total de eventos",
  passed_count: "aprovados",
  warning_count: "alertas",
  failed_count: "falhas",
  total_tokens: "tokens totais",
  total_prompt_tokens: "tokens de prompt",
  total_completion_tokens: "tokens de completion",
  total_embedding_tokens: "tokens de embedding",
  total_cost_usd: "custo total em USD",
  average_cost_usd: "custo médio em USD",
  average_quality_score: "qualidade média",
  average_duration_ms: "duração média em ms",
  provider_coverage: "coverage por provider",
  model_coverage: "coverage por modelo",
  component_coverage: "coverage por componente",
  operation_coverage: "coverage por operação",
};

const textTranslations: Record<string, string> = {
  "Structured AI execution telemetry has no recorded observability data.":
    "A telemetria estruturada de execução de IA ainda não possui dados registrados.",
  "Token and cost usage has no recorded observability data.":
    "O uso de tokens e custos ainda não possui dados registrados.",
  "Retrieval quality metrics has no recorded observability data.":
    "As métricas de qualidade de recuperação ainda não possuem dados registrados.",
  "Agent execution metrics has no recorded observability data.":
    "As métricas de execução de agentes ainda não possuem dados registrados.",
  "Multi-agent execution metrics has no recorded observability data.":
    "As métricas de execução multiagente ainda não possuem dados registrados.",

  "Record representative observability events before using the dashboard as a release signal.":
    "Registre eventos representativos de observabilidade antes de usar o dashboard como sinal de release.",

  "No evaluation telemetry risks detected.":
    "Nenhum risco de telemetria de avaliação detectado.",
  "No usage risks detected.": "Nenhum risco de uso detectado.",
  "No retrieval quality risks detected.":
    "Nenhum risco de qualidade de recuperação detectado.",
  "No agent execution risks detected.":
    "Nenhum risco de execução de agentes detectado.",
  "No multi agent execution risks detected.":
    "Nenhum risco de execução multiagente detectado.",

  "Record data for Structured AI execution telemetry before using this section for decision-making.":
    "Registre dados de telemetria estruturada de execução de IA antes de usar esta seção para tomada de decisão.",
  "Record data for Token and cost usage before using this section for decision-making.":
    "Registre dados de uso de tokens e custos antes de usar esta seção para tomada de decisão.",
  "Record data for Retrieval quality metrics before using this section for decision-making.":
    "Registre dados de qualidade de recuperação antes de usar esta seção para tomada de decisão.",
  "Record data for Agent execution metrics before using this section for decision-making.":
    "Registre dados de execução de agentes antes de usar esta seção para tomada de decisão.",
  "Record data for Multi-agent execution metrics before using this section for decision-making.":
    "Registre dados de execução multiagente antes de usar esta seção para tomada de decisão.",

  "No global observability risks detected.":
    "Nenhum risco global de observabilidade detectado.",

  "No AI usage records available.": "Nenhum registro de uso de IA disponível.",
    "No AI usage risks detected.": "Nenhum risco de uso/custo detectado.",
};

export function translateStatus(status: DashboardStatus): string {
  return statusLabels[status];
}

export function translateSectionTitle(name: string, fallbackTitle: string): string {
  return sectionTitleLabels[name] ?? fallbackTitle;
}

export function translateSectionName(name: string): string {
  return sectionTitleLabels[name] ?? name.replaceAll("_", " ");
}

export function translateMetricKey(key: string): string {
  return metricLabels[key] ?? key.replaceAll("_", " ");
}

export function translateDashboardText(text: string): string {
  return textTranslations[text] ?? text;
}
