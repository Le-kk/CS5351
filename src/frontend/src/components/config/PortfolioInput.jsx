import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Textarea } from '@/components/ui/textarea';
import { usePresentation } from '@/state/PresentationContext';

const MODES = [
  { id: 'none', label: 'No portfolio supplied', hint: 'Holdings and cash are unknown.' },
  { id: 'empty', label: 'Explicitly empty portfolio', hint: 'A known flat book: no holdings, no cash.' },
  { id: 'json', label: 'Uploaded portfolio JSON', hint: 'Parsed and validated by the backend.' },
];

const PortfolioInput = () => {
  const { form, updateForm } = usePresentation();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Portfolio input mode</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <RadioGroup
          value={form.portfolioMode}
          onValueChange={(v) => updateForm({ portfolioMode: v })}
          className="grid gap-2 sm:grid-cols-3"
        >
          {MODES.map((m) => (
            <div key={m.id} className="flex items-start space-x-2 rounded border p-3">
              <RadioGroupItem value={m.id} id={`pm-${m.id}`} className="mt-1" />
              <div>
                <Label htmlFor={`pm-${m.id}`} className="font-medium">{m.label}</Label>
                <p className="mt-0.5 text-xs text-slate-500">{m.hint}</p>
              </div>
            </div>
          ))}
        </RadioGroup>
        {form.portfolioMode === 'json' && (
          <div className="space-y-1">
            <Label htmlFor="portfolio-json">Portfolio JSON</Label>
            <input type="file" accept=".json,application/json" aria-label="Upload portfolio JSON"
              className="block w-full text-xs" onChange={async (e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                if (file.size > 32768) { e.target.value = ''; return; }
                updateForm({ portfolioText: await file.text(), portfolioFilename: file.name });
              }} />
            <Textarea
              id="portfolio-json"
              rows={6}
              className="font-mono text-xs"
              value={form.portfolioText}
              onChange={(e) => updateForm({ portfolioText: e.target.value })}
              placeholder={'{"positions": [{"ticker": "NVDA", "quantity": 10}], "cash": null}'}
            />
            <p className="text-xs text-slate-500">
              Validation is performed by the backend; errors surface during configuration validation.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PortfolioInput;
