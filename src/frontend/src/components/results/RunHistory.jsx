import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/apiClient';
import { usePresentation } from '@/state/PresentationContext';
import StatusBadge from '@/components/common/StatusBadge';
import UnavailableNotice from '@/components/common/UnavailableNotice';

// Past runs can be reopened, including their discussions and files.
const RunHistory = () => {
  const { runId, setRunId, setActiveTab } = usePresentation();
  const { data, isError, error } = useQuery({
    queryKey: ['run-history'],
    queryFn: api.getHistory,
    refetchInterval: 10000,
  });
  const runs = data?.runs || (Array.isArray(data) ? data : []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Run history</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {isError && <UnavailableNotice message={`Run history unavailable: ${error.message}`} />}
        {data && !runs.length && (
          <p className="text-sm text-slate-500">No previous runs recorded by the backend.</p>
        )}
        <ul className="divide-y">
          {runs.map((r) => {
            const id = r.runId || r.run_id || r.id;
            const isCurrent = id === runId;
            return (
              <li key={id} className="flex flex-wrap items-center justify-between gap-3 py-2">
                <div className="text-sm">
                  <span className="font-medium">{r.ticker || '—'}</span>
                  <span className="ml-2 text-xs text-slate-500">
                    {r.startedAt ? `${r.startedAt} · ` : ''}{id}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge value={r.status} />
                  <Button
                    size="sm"
                    variant={isCurrent ? 'default' : 'outline'}
                    className={isCurrent ? 'bg-emerald-600 hover:bg-emerald-700' : ''}
                    onClick={() => {
                      setRunId(id);
                      setActiveTab('live');
                    }}
                  >
                    {isCurrent ? 'Current run' : 'Open'}
                  </Button>
                </div>
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
};

export default RunHistory;
