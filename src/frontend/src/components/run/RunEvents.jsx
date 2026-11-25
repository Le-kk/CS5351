import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/apiClient';
export default function RunEvents({runId}) {
  const {data} = useQuery({queryKey:['run-events',runId], queryFn:()=>api.getEvents(runId), enabled:!!runId, refetchInterval:2000});
  return <details className="rounded-lg border bg-white p-4"><summary className="cursor-pointer text-sm font-medium">Run activity</summary><ol className="mt-3 max-h-64 space-y-2 overflow-auto text-xs">{(data || []).map((event,index)=><li key={index}><span className="mr-2 font-mono text-slate-400">{event.time?.toFixed(1)}s</span>{event.message}</li>)}</ol></details>;
}
