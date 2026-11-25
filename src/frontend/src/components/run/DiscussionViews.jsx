import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { api } from '@/lib/apiClient';
import UnavailableNotice from '@/components/common/UnavailableNotice';
import DiscussionStream from './DiscussionStream';

const TABS = [
  { id: 'analyst', label: 'Analyst reports' },
  { id: 'research', label: 'Research: Bull / Bear' },
  { id: 'trader', label: 'Trader plan' },
  { id: 'risk', label: 'Risk & final decision' },
];

const DiscussionViews = ({ runId }) => {
  const { data, isError, error } = useQuery({
    queryKey: ['run-discussions', runId],
    queryFn: () => api.getDiscussions(runId),
    enabled: !!runId,
    refetchInterval: 1500,
  });

  const records = data?.discussions || (Array.isArray(data) ? data : []);
  const groups = {};
  records.forEach((d) => {
    const cat = d.category || 'analyst';
    (groups[cat] = groups[cat] || []).push(d);
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Discussions (sanitized records from the backend)</CardTitle>
      </CardHeader>
      <CardContent>
        {isError && <UnavailableNotice message={`Discussions unavailable: ${error.message}`} />}
        {data && !records.length && (
          <p className="text-sm text-slate-500">No discussion records supplied by the backend yet.</p>
        )}
        <Tabs defaultValue="analyst">
          <TabsList className="mb-3 flex-wrap">
            {TABS.map((t) => (
              <TabsTrigger key={t.id} value={t.id}>{t.label}</TabsTrigger>
            ))}
          </TabsList>
          {TABS.map((t) => (
            <TabsContent key={t.id} value={t.id}>
              <DiscussionStream messages={groups[t.id] || []} />
            </TabsContent>
          ))}
        </Tabs>
        <p className="mt-3 text-xs text-slate-500">
          Hidden reasoning, system prompts, credentials and raw tool payloads are never exposed —
          only backend-sanitized records are shown.
        </p>
      </CardContent>
    </Card>
  );
};

export default DiscussionViews;
