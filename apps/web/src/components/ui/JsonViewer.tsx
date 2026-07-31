import type { JsonValue } from "../../types/qaAgent";

type JsonViewerProps = {
  title: string;
  value: JsonValue | Record<string, JsonValue> | JsonValue[] | null | undefined;
  emptyMessage?: string;
};

export function JsonViewer({
  emptyMessage = "Nenhum dado disponível.",
  title,
  value,
}: JsonViewerProps) {
  if (
    value === null ||
    value === undefined ||
    (Array.isArray(value) && value.length === 0) ||
    (typeof value === "object" &&
      !Array.isArray(value) &&
      Object.keys(value).length === 0)
  ) {
    return (
      <article className="json-viewer-card">
        <h3>{title}</h3>
        <p className="muted">{emptyMessage}</p>
      </article>
    );
  }

  return (
    <article className="json-viewer-card">
      <h3>{title}</h3>
      <pre>{JSON.stringify(value, null, 2)}</pre>
    </article>
  );
}
