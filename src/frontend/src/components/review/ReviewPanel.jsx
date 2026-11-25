import { useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/apiClient';
import { usePresentation } from '@/state/PresentationContext';
import ConfigSnapshot from './ConfigSnapshot';
import UnavailableNotice from '@/components/common/UnavailableNotice';

const ReviewPanel = () => {
  const { form, prepared, setPrepared, confirmed, setConfirmed, setRunId, setActiveTab } =
    usePresentation();

  const latestForm = useRef(form);
  latestForm.current = form;
  const prepareMutation = useMutation({
    mutationFn: async () => {
      const config = structuredClone(form);
      const data = await api.prepareRun({ config });
      if (JSON.stringify(config) !== JSON.stringify(latestForm.current)) throw new Error('Configuration changed during validation. Validate the current inputs again.');
      return data;
    },
    onSuccess: (data) => {
      setPrepared(data);
      setConfirmed(false);
    },
  });

  const startMutation = useMutation({
    mutationFn: () => api.startRun({ fingerprint: prepared?.fingerprint, confirmed: true }),
    onSuccess: (data) => {
      setRunId(data.runId || data.run_id);
      setPrepared(null);
      setConfirmed(false);
      setActiveTab('live');
    },
  });

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900">
        <p className="font-semibold">Before you run</p>
        <ul className="mt-1 list-disc pl-5 text-xs leading-5">
          <li>Real API calls may incur costs billed by the configured model provider.</li>
          <li>Supplied holdings may be transmitted to the configured model provider.</li>
          <li>Changing any configuration invalidates the previous confirmation.</li>
        </ul>
      </div>

      <Button
        onClick={() => prepareMutation.mutate()}
        disabled={prepareMutation.isPending}
        className="bg-emerald-600 hover:bg-emerald-700"
      >
        {prepareMutation.isPending ? 'Validating…' : 'Validate configuration with backend'}
      </Button>
      {prepareMutation.isError && <UnavailableNotice message={prepareMutation.error.message} />}

      {prepared ? (
        <ConfigSnapshot prepared={prepared} />
      ) : (
        <p className="text-sm text-slate-500">
          Not validated yet. The effective configuration, input mode, filename and frozen
          snapshot fingerprint appear here after backend validation.
        </p>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <Button
          variant="outline"
          onClick={() => setConfirmed(true)}
          disabled={!prepared || confirmed || prepareMutation.isPending}
        >
          {confirmed ? 'Confirmed — configuration frozen' : 'I confirm this configuration'}
        </Button>
        <Button
          onClick={() => startMutation.mutate()}
          disabled={!prepared || !confirmed || startMutation.isPending}
          className="bg-emerald-600 hover:bg-emerald-700"
        >
          {startMutation.isPending ? 'Starting…' : 'Start run'}
        </Button>
      </div>
      {startMutation.isError && (
        <UnavailableNotice message={`Could not start run: ${startMutation.error.message}`} />
      )}
    </div>
  );
};

export default ReviewPanel;
