import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/apiClient';
import { usePresentation } from '@/state/PresentationContext';
import StatusBadge from '@/components/common/StatusBadge';
import UnavailableNotice from '@/components/common/UnavailableNotice';
import FileBrowser from './FileBrowser';
import RunHistory from './RunHistory';

const TERMINAL = ['COMPLETED', 'INCOMPLETE', 'FAILED', 'INTERRUPTED'];

const Field = ({ label, children }) => (
  <div className="flex items-center justify-between gap-4 border-b py-2 last:border-0">
    <span className="shrink-0 text-sm text-slate-500">{label}</span>
    <span className="text-sm font-medium">{children}</span>
  </div>
);

const ResultsPanel = () => {
  const { runId } = usePresentation();
  const { data, isError, error } = useQuery({
    queryKey: ['run-status', runId],
    queryFn: () => api.getStatus(runId),
    enabled: !!runId,
    refetchInterval: (q) =>
      TERMINAL.includes(q.state.data?.status) ? false : 5000,
  });

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Run outcome{runId ? <span className="ml-2 text-xs font-normal text-slate-400">run {runId}</span> : null}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-0">
          {!runId && (
            <p className="text-sm text-slate-500">
              No run selected. <StatusBadge value="NOT_RUN" />
            </p>
          )}
          {isError && <UnavailableNotice message={`Run status unavailable: ${error.message}`} />}
          {data && (
            <>
              <Field label="Run outcome"><StatusBadge value={data.status} /></Field>
              {data.status === 'INTERRUPTED' && <p className="text-sm text-amber-800">The backend restarted. A final application verdict was not recovered; this run is not claimed as completed.</p>}
              <Field label="Final rating">
                {data.finalRating ?? <span className="text-slate-400">Not provided</span>}
              </Field>
              <Field label="Output-check status">
                <StatusBadge value={data.outputCheck || 'NOT_RUN'} />
              </Field>
              <Field label="Stop reason">
                {data.stopReason ?? <span className="text-slate-400">Not provided</span>}
              </Field>
              <p className="pt-2 text-xs text-slate-500">
                These fields are kept separate by design: a rating, or the existence of a report,
                never implies success.
              </p>
            </>
          )}
        </CardContent>
      </Card>
      <FileBrowser runId={runId} />
      <RunHistory />
    </div>
  );
};

export default ResultsPanel;
