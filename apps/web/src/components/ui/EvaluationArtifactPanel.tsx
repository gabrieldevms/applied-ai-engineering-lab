import { formatObservedAt } from "../../utils/formatObservedAt";
import { StatusBadge } from "./StatusBadge";
import type {
  EvaluationArtifact,
  EvaluationArtifactList,
  EvaluationStatus,
} from "../../types/productionObservability";

const stageLabels: Record<string, string> = {
  golden_dataset_smoke: "Golden Dataset",
  prompt_regression: "Regressão de prompts",
  llm_output_evaluation: "Avaliação da resposta LLM",
  rag_regression: "Regressão RAG",
  agent_regression: "Regressão de agentes",
  tool_calling_evaluation: "Avaliação de ferramentas",
  multi_agent_copilot_regression: "Regressão multiagente",
  llm_as_judge_evaluation: "Avaliação LLM-as-judge",
};

const evaluationStatusLabels: Record<EvaluationStatus, string> = {
  passed: "Aprovado",
  warning: "Atenção",
  failed: "Falhou",
};

function displayScore(score: number | null): string {
  return score === null ? "N/D" : `${(score * 100).toFixed(1)}%`;
}

function translateGuidance(value: string): string {
  if (value === "Review failed evaluation stages before promotion.") {
    return "Revise as etapas com falha antes da promoção.";
  }
  if (value === "Review warning evaluation stages before promotion.") {
    return "Revise os alertas das etapas antes da promoção.";
  }
  const stageResult = /^([a-z_]+) returned (warning|failed)\.$/.exec(value);
  if (stageResult) {
    return `${stageLabels[stageResult[1]] ?? stageResult[1]}: ${evaluationStatusLabels[stageResult[2] as EvaluationStatus].toLowerCase()}.`;
  }
  return value;
}

export function EvaluationArtifactPanel({
  artifactList,
  selectedId,
  onSelect,
  artifact,
  listError,
  detailError,
  lastUpdatedAt,
}: {
  artifactList: EvaluationArtifactList | null;
  selectedId: string | null;
  onSelect: (id: string) => void;
  artifact: EvaluationArtifact | null;
  listError: boolean;
  detailError: boolean;
  lastUpdatedAt: string | null;
}) {
  return (
    <section className="evaluation-details-card">
      <div className="quality-overview-heading">
        <div>
          <span className="eyebrow">Histórico persistido</span>
          <h2>Artefatos de avaliação</h2>
          <p>Resultados sanitizados das execuções determinísticas.</p>
        </div>
        <small>Atualizado: {formatObservedAt(lastUpdatedAt)}</small>
      </div>
      {listError ? (
        <p role="alert">Não foi possível atualizar a lista de artefatos.</p>
      ) : null}
      {artifactList ? (
        artifactList.artifacts.length > 0 ? (
          <div className="evaluation-artifacts-layout">
            <div className="evaluation-artifact-list" aria-label="Artefatos de avaliação">
              <p>{artifactList.total} artefato(s) · exibindo os 20 mais recentes</p>
              {artifactList.artifacts.map((item, index) => (
                <button
                  aria-pressed={item.artifact_id === selectedId}
                  className={item.artifact_id === selectedId ? "evaluation-artifact-item selected" : "evaluation-artifact-item"}
                  key={item.artifact_id}
                  onClick={() => onSelect(item.artifact_id)}
                  type="button"
                >
                  <strong>{index === 0 ? "Mais recente" : `Execução ${index + 1}`}</strong>
                  <span>{formatObservedAt(item.created_at)}</span>
                  <small>{evaluationStatusLabels[item.status]} · {item.stage_count} etapas · score {displayScore(item.score)}</small>
                </button>
              ))}
            </div>
            <div className="evaluation-artifact-detail">
              {detailError ? (
                <p role="alert">Não foi possível carregar os detalhes deste artefato.</p>
              ) : null}
              {artifact ? (
                <>
                  <div className="section-header">
                    <div>
                      <span className="eyebrow">Detalhes do artefato</span>
                      <h3>{formatObservedAt(artifact.created_at)}</h3>
                    </div>
                    <StatusBadge status={artifact.status === "passed" ? "healthy" : artifact.status === "failed" ? "critical" : "warning"} />
                  </div>
                  <p>Origem: {artifact.source === "api" ? "API" : "Script"} · Score: {displayScore(artifact.score)}</p>
                  <p>{artifact.passed_count} aprovadas · {artifact.warning_count} alertas · {artifact.failed_count} falhas</p>
                  <h4>Etapas</h4>
                  <ul className="evaluation-artifact-stages">
                    {artifact.stages.map((stage) => (
                      <li key={stage.name}>
                        <span>{stageLabels[stage.name] ?? stage.name}</span>
                        <strong>{evaluationStatusLabels[stage.status]} · {displayScore(stage.score)}</strong>
                      </li>
                    ))}
                  </ul>
                  {artifact.risks.length > 0 ? (
                    <>
                      <h4>Riscos</h4>
                      <ul>{artifact.risks.map((risk) => <li key={risk}>{translateGuidance(risk)}</li>)}</ul>
                    </>
                  ) : null}
                  {artifact.recommendations.length > 0 ? (
                    <>
                      <h4>Recomendações</h4>
                      <ul>{artifact.recommendations.map((item) => <li key={item}>{translateGuidance(item)}</li>)}</ul>
                    </>
                  ) : null}
                </>
              ) : (
                <p className="muted">Carregando detalhes do artefato selecionado.</p>
              )}
            </div>
          </div>
        ) : (
          <p className="muted">Nenhum artefato persistido ainda. Execute o pipeline de avaliação para gerar o primeiro.</p>
        )
      ) : (
        <p className="muted">Carregando histórico de avaliações.</p>
      )}
    </section>
  );
}
