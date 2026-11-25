import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PresentationProvider, usePresentation } from '@/state/PresentationContext';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/apiClient';
import ConfigurePanel from '@/components/config/ConfigurePanel';
import ReviewPanel from '@/components/review/ReviewPanel';
import LiveRunPanel from '@/components/run/LiveRunPanel';
import ResultsPanel from '@/components/results/ResultsPanel';

const TABS = [
  { id: 'configure', label: '1 · Configure' },
  { id: 'review', label: '2 · Review & Confirm' },
  { id: 'live', label: '3 · Live Run' },
  { id: 'results', label: '4 · Results & Files' },
];

const PresentationBody = () => {
  const { activeTab, setActiveTab, setRunId } = usePresentation();
  const connection = useQuery({ queryKey: ['backend-config'], queryFn: api.getConfig, staleTime: 60000 });
  const history = useQuery({ queryKey: ['active-run-recovery'], queryFn: api.getHistory, refetchInterval: 3000 });
  const activeRun = history.data?.runs?.find(run => run.status === 'RUNNING');
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
          <div>
            <h1 className="text-lg font-bold">Research Presentation Console</h1>
            <p className="text-xs text-slate-500">
              Frontend for the Python backend. Every figure, message and file shown comes from the
              backend — nothing is fabricated.
            </p>
          </div>
          <span className="rounded border px-3 py-1 text-xs text-slate-600">{connection.isError ? 'Backend unavailable' : connection.data ? 'Connected · real model execution' : 'Connecting…'}</span>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        {activeRun && <div className="mb-4 rounded border border-amber-300 bg-amber-50 p-3 text-sm">
          <p>An analysis is still running in the backend. Refreshing this page does not cancel it. Wait for it to finish before starting another run.</p>
          <button className="mt-2 underline" onClick={() => { setRunId(activeRun.runId); setActiveTab('live'); }}>View running analysis</button>
        </div>}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-4 flex-wrap">
            {TABS.map((t) => (
              <TabsTrigger key={t.id} value={t.id}>{t.label}</TabsTrigger>
            ))}
          </TabsList>
          <TabsContent value="configure"><ConfigurePanel /></TabsContent>
          <TabsContent value="review"><ReviewPanel /></TabsContent>
          <TabsContent value="live"><LiveRunPanel /></TabsContent>
          <TabsContent value="results"><ResultsPanel /></TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

const Presentation = () => (
  <PresentationProvider>
    <PresentationBody />
  </PresentationProvider>
);

export default Presentation;
