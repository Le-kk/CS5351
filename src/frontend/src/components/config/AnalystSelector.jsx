import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/apiClient';
import { usePresentation } from '@/state/PresentationContext';
import UnavailableNotice from '@/components/common/UnavailableNotice';

// Analyst options are loaded from the backend only — never hardcoded.
const AnalystSelector = () => {
  const { form, updateForm } = usePresentation();
  const { data, error } = useQuery({
    queryKey: ['backend-config'],
    queryFn: api.getConfig,
    staleTime: 60000,
  });
  const analysts = data?.analysts || [];

  const toggle = (id) =>
    updateForm({
      selectedAnalysts: form.selectedAnalysts.includes(id)
        ? form.selectedAnalysts.filter((a) => a !== id)
        : [...form.selectedAnalysts, id],
    });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Selected analysts</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {error && <UnavailableNotice message="Analyst options are supplied by the backend." />}
        <div className="grid gap-2 sm:grid-cols-2">
          {analysts.map((a) => {
            const id = a.id || a;
            const label = a.label || a;
            return (
              <div key={id} className="flex items-center space-x-2">
                <Checkbox
                  id={`analyst-${id}`}
                  checked={form.selectedAnalysts.includes(id)}
                  onCheckedChange={() => toggle(id)}
                />
                <Label htmlFor={`analyst-${id}`} className="cursor-pointer font-normal">
                  {label}
                </Label>
              </div>
            );
          })}
        </div>
        {!error && !analysts.length && (
          <p className="text-sm text-slate-500">No analysts reported by the backend yet.</p>
        )}
      </CardContent>
    </Card>
  );
};

export default AnalystSelector;
