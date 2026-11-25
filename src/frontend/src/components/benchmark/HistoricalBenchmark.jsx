import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/apiClient';
import UnavailableNotice from '@/components/common/UnavailableNotice';

export default function HistoricalBenchmark() {
  const {data, isError} = useQuery({queryKey: ['benchmark-historical'], queryFn: api.getHistoricalBenchmark, staleTime: 300000});
  if (isError) return <UnavailableNotice message="Historical evidence is unavailable from the backend. No fallback numbers are substituted." />;
  if (!data) return <p className="text-sm text-slate-500">Loading recorded benchmark evidence…</p>;
  const metrics = [ ['Same-day control', data.controlTotalTokens?.toLocaleString(), '1 recorded run'],
    ['Optimized average', data.optimizedAverageTokens?.toLocaleString(), `${data.optimizedRunCount} recorded runs`],
    ['Fewer total tokens', `${data.reductionPercent}%`, 'Historical case only'] ];
  return <div className="space-y-4"><Card><CardHeader><CardTitle>Historical token experiment — {data.context?.case?.ticker}</CardTitle><p className="text-xs text-slate-500">Backend-loaded provider usage. Measurement date: {data.context?.date}; analysis date: {data.context?.case?.analysis_date}.</p></CardHeader><CardContent className="grid gap-3 sm:grid-cols-3">{metrics.map(([name,value,note])=><div className="rounded-lg border p-4 text-center" key={name}><p className="text-xs text-slate-500">{name}</p><p className="my-2 text-2xl font-bold text-emerald-700">{value ?? 'Unavailable'}</p><p className="text-xs text-slate-500">{note}</p></div>)}</CardContent></Card><p className="text-sm text-slate-600">This historical comparison is separate from the current run. It is not a general reduction, a token ceiling, or proof of unchanged output quality.</p><p className="text-xs text-slate-500">Source: {data.context?.source}</p><ul className="list-disc space-y-1 pl-5 text-xs text-slate-500">{data.context?.limitations?.map(item=><li key={item}>{item}</li>)}</ul></div>;
}
