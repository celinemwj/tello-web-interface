import ImmersivePageLayout from "../components/layout/ImmersivePageLayout";
import MonitoringPanel from "../components/MonitoringPanel";

export default function MonitoringPage() {
  return (
    <ImmersivePageLayout
      title="Drone monitoring"
      subtitle="Visualize the latest drone state, telemetry data and execution logs."
    >
      <MonitoringPanel />
    </ImmersivePageLayout>
  );
}