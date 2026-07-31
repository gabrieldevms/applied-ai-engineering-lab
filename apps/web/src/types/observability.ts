export type DashboardStatus = "healthy" | "warning" | "critical" | "empty";

export type DashboardSectionStatus =
  | "healthy"
  | "warning"
  | "critical"
  | "empty";

export type DashboardMetricValue =
  | string
  | number
  | boolean
  | null
  | DashboardMetricValue[]
  | { [key: string]: DashboardMetricValue };

export type ObservabilityDashboardSection = {
  name: string;
  title: string;
  status: DashboardSectionStatus;
  metrics: Record<string, DashboardMetricValue>;
  risks: string[];
  recommendations: string[];
  metadata: Record<string, DashboardMetricValue>;
};

export type ObservabilityDashboardResponse = {
  status: DashboardStatus;
  generated_at: string;
  sections: ObservabilityDashboardSection[];
  global_risks: string[];
  recommendations: string[];
  metadata: Record<string, DashboardMetricValue>;
};
