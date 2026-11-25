import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { api } from '@/lib/apiClient';
import { usePresentation } from '@/state/PresentationContext';
import AnalystSelector from './AnalystSelector';
import PortfolioInput from './PortfolioInput';
import UnavailableNotice from '@/components/common/UnavailableNotice';

const RoundsSelect = ({ label, value, onChange, max }) => (
  <div className="space-y-1">
    <Label>{label}</Label>
    <Select value={String(value)} onValueChange={(v) => onChange(Number(v))}>
      <SelectTrigger><SelectValue /></SelectTrigger>
      <SelectContent>
        {Array.from({ length: max }, (_, i) => (
          <SelectItem key={i + 1} value={String(i + 1)}>{i + 1}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  </div>
);

const ModelSelect = ({ label, value, onChange, models }) => (
  <div className="space-y-1">
    <Label>{label}</Label>
    <Select value={value} onValueChange={onChange} disabled={!models.length}>
      <SelectTrigger>
        <SelectValue placeholder={models.length ? 'Select model' : 'Backend unavailable'} />
      </SelectTrigger>
      <SelectContent>
        {models.map((m) => (
          <SelectItem key={m.id || m} value={m.id || m}>{m.label || m}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  </div>
);

const ConfigurePanel = () => {
  const { form, updateForm } = usePresentation();
  const { data, error } = useQuery({
    queryKey: ['backend-config'],
    queryFn: api.getConfig,
    staleTime: 60000,
  });
  const models = data?.models || [];
  const maxRounds = data?.limits?.maxRounds || 5;
  useEffect(() => {
    if (!data || form.defaultsLoaded) return;
    updateForm({ ...data.defaults, defaultsLoaded: true });
  }, [data, form.defaultsLoaded, updateForm]);

  return (
    <div className="space-y-4">
      {error && (
        <UnavailableNotice message="Model choices and limits must come from the backend. Model selection is disabled until the backend is reachable." />
      )}
      <Card>
        <CardHeader><CardTitle className="text-base">Analysis target</CardTitle></CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          <div className="space-y-1">
            <Label htmlFor="ticker">Ticker</Label>
            <Input id="ticker" value={form.ticker} placeholder="e.g. NVDA"
              onChange={(e) => updateForm({ ticker: e.target.value.toUpperCase() })} />
          </div>
          <div className="space-y-1">
            <Label htmlFor="date">Analysis date (YYYY-MM-DD)</Label>
            <Input id="date" type="text" inputMode="numeric" placeholder="2026-01-09" value={form.analysisDate}
              onChange={(e) => updateForm({ analysisDate: e.target.value })} />
          </div>
        </CardContent>
      </Card>
      <AnalystSelector />
      <Card>
        <CardHeader><CardTitle className="text-base">Models and rounds</CardTitle></CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          <ModelSelect label="Deep / debate model (backend-approved)" value={form.deepModel}
            models={models} onChange={(v) => updateForm({ deepModel: v })} />
          <ModelSelect label="Quick model (backend-approved)" value={form.quickModel}
            models={models} onChange={(v) => updateForm({ quickModel: v })} />
          <RoundsSelect label="Research debate rounds" value={form.researchRounds}
            onChange={(v) => updateForm({ researchRounds: v })} max={maxRounds} />
          <RoundsSelect label="Risk discussion rounds" value={form.riskRounds}
            onChange={(v) => updateForm({ riskRounds: v })} max={maxRounds} />
          <div className="space-y-1">
            <Label htmlFor="limit">Model-request limit (optional)</Label>
            <Input id="limit" type="number" min="0" value={form.maxModelRequests}
              onChange={(e) => updateForm({ maxModelRequests: e.target.value })}
              placeholder="Leave empty for no limit" />
          </div>
        </CardContent>
      </Card>
      <PortfolioInput />
    </div>
  );
};

export default ConfigurePanel;
