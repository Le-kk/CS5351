import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/apiClient';
import { usePresentation } from '@/state/PresentationContext';
import StatusBadge from '@/components/common/StatusBadge';
import UsagePanel from './UsagePanel';
import DiscussionViews from './DiscussionViews';
import RunEvents from './RunEvents';

const TERMINAL = ['COMPLETED', 'INCOMPLETE', 'FAILED', 'INTERRUPTED'];
const fmtElapsed = (s) => `${Math.floor(s / 60)}m ${String(Math.floor(s % 60)).padStart(2, '0')}s`;

const LiveRunPanel = () => {
  const { runId } = usePresentation();
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  const { data, isError, error } = useQuery({
    queryKey: ['run-status', runId],
    queryFn: () => api.getStatus(runId),
    enabled: !!runId,
    refetchInterval: (query) =>
      TERMINAL.includes(query.state.data?.status) ? false : 3000,
  });

  if (!runId) {
    return (
      <Card>
        <CardContent className="p-6 text-sm text-slate-500">
          No run started yet. Complete Configure → Review & Confirm, then start a run.{' '}
          <StatusBadge value="NOT_RUN" />
        </CardContent>
      </Card>
    );
  }

  const startedAt = data?.startedAt ? new Date(data.startedAt).getTime() : null;
  const elapsed = data?.elapsedSeconds ?? (startedAt ? Math.floor((now - startedAt) / 1000) : null);

  return (
    <div className="space-y-4">
      {isError && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-800">
          <p className="font-semibold">Live connection lost</p>
          <p className="mt-0.5 text-xs">
            {error.message}. Run state is unknown until the connection is restored — this is NOT
            displayed as a successful or failed model run.
          </p>
        </div>
      )}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Execution status — run {runId}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-4">
          <div>
            <p className="text-xs text-slate-500">Status</p>
            <StatusBadge value={data?.status} />
          </div>
          <div>
            <p className="text-xs text-slate-500">Current agent / stage</p>
            <p className={`text-sm font-medium ${data?.currentAgent || data?.currentStage ? '' : 'text-slate-400'}`}>
              {data?.currentAgent || data?.currentStage || 'Not reported'}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Elapsed time</p>
            <p className={`text-sm font-medium ${elapsed == null ? 'text-slate-400' : ''}`}>
              {elapsed == null ? 'Unavailable' : fmtElapsed(elapsed)}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Model calls</p>
            <p className={`text-sm font-medium ${data?.modelCalls == null ? 'text-slate-400' : ''}`}>
              {data?.modelCalls ?? 'Unavailable'}
            </p>
          </div>
        </CardContent>
      </Card>
      <UsagePanel usage={data?.usage} />
      <DiscussionViews runId={runId} />
      <RunEvents runId={runId} />
    </div>
  );
};

export default LiveRunPanel;
