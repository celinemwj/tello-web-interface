import ImmersivePageLayout from "../components/layout/ImmersivePageLayout";
import CommandPanel from "../components/CommandPanel";

export default function CommandPage() {
  return (
    <ImmersivePageLayout
      title="AI mission console"
      subtitle="Translate natural-language missions into safe drone actions."
    >
      <CommandPanel />
    </ImmersivePageLayout>
  );
}