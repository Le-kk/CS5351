import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import StatusBadge from '@/components/common/StatusBadge';

const Row = ({ label, children, mono }) => (
  <div className="flex justify-between gap-4 border-b py-1.5 last:border-0">
    <span className="shrink-0 text-sm text-slate-500">{label}</span>
    <span className={`break-all text-right text-sm ${mono ? 'font-mono text-xs' : ''}`}>{children}</span>
  </div>
);

// Shows only what the backend validated and returned — nothing is inferred locally.
const ConfigSnapshot = ({ prepared }) => (
  <Card>
    <CardHeader className="flex-row items-center justify-between space-y-0">
      <CardTitle className="text-base">Backend-validated snapshot</CardTitle>
      <StatusBadge
        value={prepared.fingerprint ? 'PASSED' : 'NOT_RUN'}
        label={prepared.fingerprint ? 'VALIDATED' : 'NOT VALIDATED'}
      />
    </CardHeader>
    <CardContent className="space-y-0">
      <Row label="Input mode">{prepared.inputMode || '—'}</Row>
      <Row label="Filename">{prepared.filename || '—'}</Row>
      <Row label="Configuration fingerprint" mono>{prepared.fingerprint || '—'}</Row>
      <Row label="Portfolio fingerprint" mono>{prepared.portfolioFingerprint || 'Not applicable (no portfolio)'}</Row>
      <Row label="Effective configuration">
        <pre className="max-h-40 overflow-auto rounded bg-slate-50 p-2 text-left text-xs">
          {JSON.stringify(prepared.effectiveConfig ?? prepared, null, 2)}
        </pre>
      </Row>
    </CardContent>
  </Card>
);

export default ConfigSnapshot;
