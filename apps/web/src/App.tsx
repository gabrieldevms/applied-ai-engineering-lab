import { useEffect, useMemo, useState } from "react";
import { apiGet, apiPost } from "./services/apiClient";
import {
  sampleDatabaseSchema,
  sampleRequirement,
  sampleSqlRegressionSuite,
  sampleTableData,
} from "./samples";

type Tab = "dashboard" | "qa-agent" | "data-analyst";

type DashboardState = {
  health?: unknown;
  providers?: unknown;
  tools?: unknown;
  specializedAgents?: unknown;
};

function JsonViewer({ value }: { value: unknown }) {
  return (
    <pre className="json-viewer">
      {value === undefined ? "No data yet." : JSON.stringify(value, null, 2)}
    </pre>
  );
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return <label className="field-label">{children}</label>;
}

function parseJsonInput(value: string, fieldName: string): unknown {
  try {
    return JSON.parse(value);
  } catch {
    throw new Error(`${fieldName} must be valid JSON.`);
  }
}

function DashboardPage() {
  const [state, setState] = useState<DashboardState>({});
  const [loading, setLoading] = useState(false);

  async function loadDashboard() {
    setLoading(true);

    const [health, providers, tools, specializedAgents] = await Promise.all([
      apiGet("/health"),
      apiGet("/llm/providers"),
      apiGet("/agents/tools"),
      apiGet("/agents/specialized"),
    ]);

    setState({
      health,
      providers,
      tools,
      specializedAgents,
    });

    setLoading(false);
  }

  useEffect(() => {
    void loadDashboard();
  }, []);

  return (
    <section className="page-grid">
      <div className="panel hero-panel">
        <p className="eyebrow">Local Lab Console</p>
        <h2>Applied AI Engineering Lab</h2>
        <p>
          Console local para explorar o backend, visualizar agentes, tools,
          providers e fluxos de QA/Data Analysis sem usar somente Swagger.
        </p>

        <button onClick={loadDashboard} disabled={loading}>
          {loading ? "Loading..." : "Refresh status"}
        </button>
      </div>

      <div className="panel">
        <h3>API Health</h3>
        <JsonViewer value={state.health} />
      </div>

      <div className="panel">
        <h3>LLM Providers</h3>
        <JsonViewer value={state.providers} />
      </div>

      <div className="panel">
        <h3>Agent Tools</h3>
        <JsonViewer value={state.tools} />
      </div>

      <div className="panel">
        <h3>Specialized Agents</h3>
        <JsonViewer value={state.specializedAgents} />
      </div>
    </section>
  );
}

function QAAgentPage() {
  const [requirementText, setRequirementText] = useState(sampleRequirement);
  const [mode, setMode] = useState("auto");
  const [schemaJson, setSchemaJson] = useState(
    JSON.stringify(sampleDatabaseSchema, null, 2),
  );
  const [tableDataJson, setTableDataJson] = useState(
    JSON.stringify(sampleTableData, null, 2),
  );
  const [result, setResult] = useState<unknown>();
  const [evaluation, setEvaluation] = useState<unknown>();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);

  const canEvaluate = useMemo(() => {
    return typeof result === "object" && result !== null;
  }, [result]);

  async function runQAAgent() {
    setLoading(true);
    setError(undefined);
    setEvaluation(undefined);

    try {
      const databaseSchema = parseJsonInput(schemaJson, "Database schema");
      const tableData = parseJsonInput(tableDataJson, "Table data");

      const response = await apiPost("/agents/qa/run", {
        requirement_text: requirementText,
        language: "pt-BR",
        max_steps: 6,
        data_validation: {
          objective: "Validar dados relacionados ao requisito informado.",
          mode,
          database_schema: databaseSchema,
          table_data: tableData,
          max_rows: 100,
        },
      });

      if (!response.ok) {
        setError(response.error ?? "QA Agent request failed.");
        setResult(undefined);
        return;
      }

      setResult(response.data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error ? caughtError.message : "Unknown error",
      );
      setResult(undefined);
    } finally {
      setLoading(false);
    }
  }

  async function evaluateQAAgent() {
    if (!result) {
      return;
    }

    setLoading(true);
    setError(undefined);

    const response = await apiPost("/agents/qa/evaluate", {
      agent_response: result,
      expected_status: "completed",
      expect_data_validation: mode !== "disabled",
      expected_data_row_count: mode === "disabled" ? undefined : 2,
      expected_data_columns:
        mode === "disabled" ? [] : ["account_id", "final_balance"],
      metadata: {
        source: "local-web-console",
      },
    });

    if (!response.ok) {
      setError(response.error ?? "QA Agent evaluation failed.");
      setEvaluation(undefined);
      setLoading(false);
      return;
    }

    setEvaluation(response.data);
    setLoading(false);
  }

  return (
    <section className="page-grid two-columns">
      <div className="panel">
        <p className="eyebrow">QA Agent</p>
        <h2>Requirement + Data Validation</h2>

        <FieldLabel>Requirement text</FieldLabel>
        <textarea
          value={requirementText}
          onChange={(event) => setRequirementText(event.target.value)}
          rows={6}
        />

        <FieldLabel>Data validation mode</FieldLabel>
        <select value={mode} onChange={(event) => setMode(event.target.value)}>
          <option value="auto">auto</option>
          <option value="required">required</option>
          <option value="disabled">disabled</option>
        </select>

        <FieldLabel>Database schema JSON</FieldLabel>
        <textarea
          value={schemaJson}
          onChange={(event) => setSchemaJson(event.target.value)}
          rows={14}
          className="code-input"
        />

        <FieldLabel>Table data JSON</FieldLabel>
        <textarea
          value={tableDataJson}
          onChange={(event) => setTableDataJson(event.target.value)}
          rows={14}
          className="code-input"
        />

        <div className="button-row">
          <button onClick={runQAAgent} disabled={loading}>
            {loading ? "Running..." : "Run QA Agent"}
          </button>

          <button
            className="secondary-button"
            onClick={evaluateQAAgent}
            disabled={loading || !canEvaluate}
          >
            Evaluate Response
          </button>
        </div>

        {error && <div className="error-box">{error}</div>}
      </div>

      <div className="panel">
        <h3>QA Agent Response</h3>
        <JsonViewer value={result} />

        <h3>Evaluation</h3>
        <JsonViewer value={evaluation} />
      </div>
    </section>
  );
}

function DataAnalystPage() {
  const [question, setQuestion] = useState("Qual é o saldo final por conta?");
  const [schemaJson, setSchemaJson] = useState(
    JSON.stringify(sampleDatabaseSchema, null, 2),
  );
  const [tableDataJson, setTableDataJson] = useState(
    JSON.stringify(sampleTableData, null, 2),
  );
  const [workflowResult, setWorkflowResult] = useState<unknown>();
  const [agentResult, setAgentResult] = useState<unknown>();
  const [regressionResult, setRegressionResult] = useState<unknown>();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);

  async function runSqlWorkflow() {
    setLoading(true);
    setError(undefined);

    try {
      const databaseSchema = parseJsonInput(schemaJson, "Database schema");
      const tableData = parseJsonInput(tableDataJson, "Table data");

      const response = await apiPost("/data-analysis/sql/run", {
        question,
        language: "pt-BR",
        max_rows: 100,
        database_schema: databaseSchema,
        table_data: tableData,
      });

      if (!response.ok) {
        setError(response.error ?? "SQL workflow failed.");
        setWorkflowResult(undefined);
        return;
      }

      setWorkflowResult(response.data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error ? caughtError.message : "Unknown error",
      );
      setWorkflowResult(undefined);
    } finally {
      setLoading(false);
    }
  }

  async function runDataAnalystAgent() {
    setLoading(true);
    setError(undefined);

    try {
      const databaseSchema = parseJsonInput(schemaJson, "Database schema");
      const tableData = parseJsonInput(tableDataJson, "Table data");

      const response = await apiPost("/data-analysis/agent/run", {
        objective: question,
        language: "pt-BR",
        max_rows: 100,
        database_schema: databaseSchema,
        table_data: tableData,
      });

      if (!response.ok) {
        setError(response.error ?? "Data Analyst Agent failed.");
        setAgentResult(undefined);
        return;
      }

      setAgentResult(response.data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error ? caughtError.message : "Unknown error",
      );
      setAgentResult(undefined);
    } finally {
      setLoading(false);
    }
  }

  async function runRegressionSuite() {
    setLoading(true);
    setError(undefined);

    const response = await apiPost(
      "/data-analysis/sql/regression/run",
      sampleSqlRegressionSuite,
    );

    if (!response.ok) {
      setError(response.error ?? "SQL regression suite failed.");
      setRegressionResult(undefined);
      setLoading(false);
      return;
    }

    setRegressionResult(response.data);
    setLoading(false);
  }

  return (
    <section className="page-grid two-columns">
      <div className="panel">
        <p className="eyebrow">Data Analyst Agent</p>
        <h2>SQL Workflow Console</h2>

        <FieldLabel>Question / objective</FieldLabel>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          rows={4}
        />

        <FieldLabel>Database schema JSON</FieldLabel>
        <textarea
          value={schemaJson}
          onChange={(event) => setSchemaJson(event.target.value)}
          rows={14}
          className="code-input"
        />

        <FieldLabel>Table data JSON</FieldLabel>
        <textarea
          value={tableDataJson}
          onChange={(event) => setTableDataJson(event.target.value)}
          rows={14}
          className="code-input"
        />

        <div className="button-row">
          <button onClick={runSqlWorkflow} disabled={loading}>
            Run SQL Workflow
          </button>

          <button
            className="secondary-button"
            onClick={runDataAnalystAgent}
            disabled={loading}
          >
            Run Agent
          </button>

          <button
            className="secondary-button"
            onClick={runRegressionSuite}
            disabled={loading}
          >
            Run Regression
          </button>
        </div>

        {error && <div className="error-box">{error}</div>}
      </div>

      <div className="panel">
        <h3>SQL Workflow Result</h3>
        <JsonViewer value={workflowResult} />

        <h3>Data Analyst Agent Result</h3>
        <JsonViewer value={agentResult} />

        <h3>SQL Regression Result</h3>
        <JsonViewer value={regressionResult} />
      </div>
    </section>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState<Tab>("dashboard");

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Prototype UI</p>
          <h1>AI Lab Console</h1>
        </div>

        <nav className="tab-nav">
          <button
            className={activeTab === "dashboard" ? "active" : ""}
            onClick={() => setActiveTab("dashboard")}
          >
            Dashboard
          </button>
          <button
            className={activeTab === "qa-agent" ? "active" : ""}
            onClick={() => setActiveTab("qa-agent")}
          >
            QA Agent
          </button>
          <button
            className={activeTab === "data-analyst" ? "active" : ""}
            onClick={() => setActiveTab("data-analyst")}
          >
            Data Analyst
          </button>
        </nav>
      </header>

      {activeTab === "dashboard" && <DashboardPage />}
      {activeTab === "qa-agent" && <QAAgentPage />}
      {activeTab === "data-analyst" && <DataAnalystPage />}
    </main>
  );
}

export default App;
