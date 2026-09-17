export function formatObservedAt(value: string | null): string {
  if (!value) {
    return "Sem registro";
  }
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(new Date(value));
}
