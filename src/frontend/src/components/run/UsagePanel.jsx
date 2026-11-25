import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const Cell = ({ label, value }) => (
  <div className="rounded border p-3 text-center">
    <p className="text-xs text-slate-500">{label}</p>
    <p className={`mt-1 text-lg font-semibold ${value == null ? 'text-slate-400' : 'text-emerald-700'}`}>
      {value == null ? 'Unavailable' : value.toLocaleString()}
    </p>
  </div>
);

// Provider-reported usage only. Missing figures appear as Unavailable/Partial —
// never as invented zeros.
const UsagePanel = ({ usage }) => {
  const input = usage?.inputTokens ?? usage?.input_tokens ?? null;
  const output = usage?.outputTokens ?? usage?.output_tokens ?? null;
  const total = usage?.totalTokens ?? usage?.total_tokens ?? null;
  const present = [input, output, total].filter((v) => v != null).length;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">
          {present === 0
            ? 'Provider usage: Unavailable'
            : present < 3 || usage?.complete === false
              ? 'Provider usage: Partial'
              : 'Provider-reported token usage'}
        </CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-3 gap-3">
        <Cell label="Input tokens" value={input} />
        <Cell label="Output tokens" value={output} />
        <Cell label="Total tokens" value={total} />
      </CardContent>
      <p className="px-6 pb-4 text-xs text-slate-500">
        Values are reported by the model provider through the backend. Missing figures are never
        displayed as zero.
      </p>
    </Card>
  );
};

export default UsagePanel;
