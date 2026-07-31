import { useMemo, useState } from "react";
import { runDataAnalystAgent } from "../api/dataAnalystApi";
import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import type {
  DataAnalystAgentRequest,
  DataAnalystAgentResponse,
  DatabaseSchema,
  DatabaseTableData,
  SQLExecutionResponse,
} from "../types/dataAnalyst";
import type { JsonValue } from "../types/qaAgent";

type RequestState = "idle" | "loading" | "error";

const defaultObjective =
  "Quais acordos de renegociação estão pendentes de emissão de boleto?";

const defaultDatabaseSchemaJson = `{
  "name": "debt_renegotiation",
  "description": "Schema simplificado para análise de renegociação de dívidas.",
  "tables": [
    {
      "name": "agreements",
      "description": "Acordos de renegociação gerados para clientes.",
      "columns": [
        {
          "name": "agreement_id",
          "data_type": "integer",
          "primary_key": true
        },
        {
          "name": "customer_id",
          "data_type": "integer"
        },
        {
          "name": "status",
          "data_type": "text"
        },
        {
          "name": "installment_count",
          "data_type": "integer"
        },
        {
          "name": "total_amount",
          "data_type": "decimal"
        },
        {
          "name": "boleto_status",
          "data_type": "text"
        }
      ],
      "metadata": {
        "domain": "banking"
      }
    }
  ],
  "metadata": {
    "source": "ai-quality-command-center"
  }
}`;

const defaultTableDataJson = `[
  {
    "table_name": "agreements",
    "rows": [
      {
        "agreement_id": 1001,
        "customer_id": 501,
        "status": "active",
        "installment_count": 6,
        "total_amount": 1250.75,
        "boleto_status": "pending"
      },
      {
        "agreement_id": 1002,
        "customer_id": 502,
        "status": "active",
        "installment_count": 3,
        "total_amount": 800,
        "boleto_status": "issued"
      },
      {
        "agreement_id": 1003,
        "customer_id": 503,
        "status": "cancelled",
        "installment_count": 10,
        "total_amount": 2100,
        "boleto_status": "pending"
      }
    ],
    "metadata": {
      "fixture": "demo"
    }
  }
]`;

function parseDatabaseSchema(value: string): DatabaseSchema {
  const parsedValue = JSON.parse(value) as DatabaseSchema;

  if (
    parsedValue === null ||
    Array.isArray(parsedValue) ||
    typeof parsedValue !== "object" ||
    typeof parsedValue.name !== "string" ||
    !Array.isArray(parsedValue.tables)
  ) {
    throw new Error(
      "O database_schema precisa ser um objeto com name e tables.",
    );
  }

  return parsedValue;
}

function parseTableData(value: string): DatabaseTableData[] {
  const parsedValue = JSON.parse(value) as unknown;

  if (!Array.isArray(parsedValue)) {
    throw new Error("O table_data precisa ser um array JSON.");
  }

  return parsedValue as DatabaseTableData[];
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Erro inesperado ao executar o Data Analyst Agent.";
}

function formatStatusLabel(status: string): string {
  return status.replaceAll("_", " ");
}

function getGeneratedSql(response: DataAnalystAgentResponse): string {
  return response.workflow.generation.candidate.sql;
}

function getSqlExplanation(response: DataAnalystAgentResponse): string {
  return response.workflow.generation.candidate.explanation;
}

function getExecution(response: DataAnalystAgentResponse): SQLExecutionResponse | null {
  return response.workflow.execution ?? null;
}

function getTableCount(schemaJson: string): number {
  try {
    return parseDatabaseSchema(schemaJson).tables.length;
  } catch {
    return 0;
  }
}

function getInputRowCount(tableDataJson: string): number {
  try {
    return parseTableData(tableDataJson).reduce((total, table) => {
      return total + table.rows.length;
    }, 0);
  } catch {
    return 0;
  }
}

function renderRowsTable(rows: Record<string, JsonValue>[]) {
  if (rows.length === 0) {
    return <p className="muted">Nenhuma linha retornada.</p>;
  }

  const columns = Object.keys(rows[0] ?? {});

  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column) => (
                <td key={column}>{String(row[column] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function DataAnalystConsolePage() {
  const [objective, setObjective] = useState(defaultObjective);
  const [databaseSchemaJson, setDatabaseSchemaJson] = useState(
    defaultDatabaseSchemaJson,
  );
  const [tableDataJson, setTableDataJson] = useState(defaultTableDataJson);
  const [language, setLanguage] = useState("pt-BR");
  const [maxRows, setMaxRows] = useState(100);
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [response, setResponse] = useState<DataAnalystAgentResponse | null>(
    null,
  );

  const tableCount = useMemo(() => {
    return getTableCount(databaseSchemaJson);
  }, [databaseSchemaJson]);

  const inputRowCount = useMemo(() => {
    return getInputRowCount(tableDataJson);
  }, [tableDataJson]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setRequestState("loading");
    setErrorMessage(null);
    setResponse(null);

    try {
      const databaseSchema = parseDatabaseSchema(databaseSchemaJson);
      const tableData = parseTableData(tableDataJson);

      const payload: DataAnalystAgentRequest = {
        objective,
        database_schema: databaseSchema,
        table_data: tableData,
        language,
        max_rows: maxRows,
        metadata: {
          source: "ai-quality-command-center",
          console: "data-analyst",
        },
      };

      const result = await runDataAnalystAgent(payload);

      setResponse(result);
      setRequestState("idle");
    } catch (error) {
      setRequestState("error");
      setErrorMessage(getErrorMessage(error));
    }
  }

  const execution = response ? getExecution(response) : null;

  return (
    <div className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Data Analyst</span>
          <h1>Data Analyst Console</h1>
          <p>
            Execute perguntas em linguagem natural sobre dados tabulares, gere
            SQL read-only, valide segurança, execute em SQLite em memória e
            visualize evidências de resultado.
          </p>
        </div>
      </section>

      <section className="console-layout">
        <form className="console-form-card" onSubmit={(event) => void handleSubmit(event)}>
          <div>
            <span className="eyebrow">Input</span>
            <h2>Executar Data Analyst Agent</h2>
            <p>
              Informe objetivo, schema e dados de tabela. O console envia o
              payload para <code>POST /data-analysis/agent/run</code>.
            </p>
          </div>

          <label className="form-field">
            <span>Objective</span>
            <textarea
              onChange={(event) => setObjective(event.target.value)}
              rows={5}
              value={objective}
            />
          </label>

          <label className="form-field">
            <span>Database schema JSON</span>
            <textarea
              onChange={(event) => setDatabaseSchemaJson(event.target.value)}
              rows={14}
              value={databaseSchemaJson}
            />
          </label>

          <label className="form-field">
            <span>Table data JSON</span>
            <textarea
              onChange={(event) => setTableDataJson(event.target.value)}
              rows={14}
              value={tableDataJson}
            />
          </label>

          <div className="form-grid">
            <label className="form-field">
              <span>Language</span>
              <input
                onChange={(event) => setLanguage(event.target.value)}
                value={language}
              />
            </label>

            <label className="form-field">
              <span>Max rows</span>
              <input
                min={1}
                max={1000}
                onChange={(event) => setMaxRows(Number(event.target.value))}
                type="number"
                value={maxRows}
              />
            </label>
          </div>

          <button
            className="primary-button"
            disabled={requestState === "loading"}
            type="submit"
          >
            {requestState === "loading"
              ? "Executando..."
              : "Run Data Analyst"}
          </button>
        </form>

        <section className="console-result-stack">
          {requestState === "error" ? (
            <article className="alert-card">
              <strong>Não foi possível executar o Data Analyst Agent.</strong>
              <p>
                Verifique o JSON de schema, os dados de tabela e se a API está
                rodando.
              </p>
              <small>{errorMessage}</small>
            </article>
          ) : null}

          <section className="metrics-grid">
            <MetricCard
              description="Tabelas definidas no schema informado"
              label="Tables"
              value={tableCount}
            />
            <MetricCard
              description="Linhas de entrada carregadas no SQLite em memória"
              label="Input rows"
              value={inputRowCount}
            />
            <MetricCard
              description="Status do Data Analyst Agent"
              label="Status"
              value={response?.status ?? "not_run"}
            />
            <MetricCard
              description="Linhas retornadas pela consulta"
              label="Result rows"
              value={response?.evidence?.row_count ?? 0}
            />
          </section>

          {response ? (
            <>
              <article className="console-answer-card">
                <span className="eyebrow">{response.agent_name}</span>
                <h2>Resposta do Data Analyst</h2>
                <p>{response.answer}</p>
              </article>

              <section className="data-analyst-sql-card">
                <div>
                  <span className="eyebrow">Generated SQL</span>
                  <h2>Consulta gerada</h2>
                  <p>{getSqlExplanation(response)}</p>
                </div>

                <pre>{getGeneratedSql(response)}</pre>
              </section>

              <section className="content-grid">
                <JsonViewer
                  title="SQL safety validation"
                  value={response.workflow.generation.validation}
                />

                <JsonViewer
                  title="SQL generation metadata"
                  value={response.workflow.generation.metadata}
                />
              </section>

              {execution ? (
                <section className="console-steps-card">
                  <div>
                    <span className="eyebrow">Execution result</span>
                    <h2>Resultado da consulta</h2>
                    <p className="muted">
                      Status: {formatStatusLabel(execution.status)} · Rows:{" "}
                      {execution.row_count} · Truncated:{" "}
                      {execution.truncated ? "yes" : "no"}
                    </p>
                  </div>

                  {renderRowsTable(execution.rows)}
                </section>
              ) : (
                <section className="empty-state">
                  <h2>Consulta não executada</h2>
                  <p>
                    O workflow não retornou execução. Isso normalmente acontece
                    quando o SQL é bloqueado pela validação de segurança.
                  </p>
                </section>
              )}

              <section className="content-grid">
                <JsonViewer
                  title="Evidence"
                  value={response.evidence}
                  emptyMessage="Nenhuma evidência de execução foi retornada."
                />

                <JsonViewer title="Workflow" value={response.workflow} />
              </section>

              <section className="console-steps-card">
                <div>
                  <span className="eyebrow">Trace</span>
                  <h2>Execution trace</h2>
                </div>

                <div className="data-analyst-trace-list">
                  {response.trace.map((step, index) => (
                    <article
                      className="data-analyst-trace-card"
                      key={`${index}-${step.step}`}
                    >
                      <div>
                        <span className="eyebrow">Step {index + 1}</span>
                        <h3>{step.step}</h3>
                        <p>{step.message}</p>
                      </div>

                      <span className="status-badge status-empty">
                        {formatStatusLabel(step.status)}
                      </span>
                    </article>
                  ))}
                </div>
              </section>

              <JsonViewer title="Metadata" value={response.metadata} />
            </>
          ) : (
            <section className="empty-state">
              <h2>Nenhuma análise realizada ainda</h2>
              <p>
                Execute o Data Analyst Agent para visualizar SQL gerado,
                validação read-only, resultado tabular, evidências e trace.
              </p>
            </section>
          )}
        </section>
      </section>
    </div>
  );
}
