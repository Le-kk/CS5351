import { cn } from '@/lib/utils';

const STYLES = {
  COMPLETED: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  PASSED: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  INCOMPLETE: 'bg-amber-100 text-amber-800 border-amber-300',
  NEEDS_REVIEW: 'bg-amber-100 text-amber-800 border-amber-300',
  NOT_RUN: 'bg-slate-100 text-slate-600 border-slate-300',
  FAILED: 'bg-red-100 text-red-700 border-red-300',
  RUNNING: 'bg-blue-100 text-blue-700 border-blue-300',
};

const StatusBadge = ({ value, label }) => {
  const v = value || 'NOT_RUN';
  return (
    <span
      className={cn(
        'inline-flex items-center rounded border px-2 py-0.5 text-xs font-semibold tracking-wide',
        STYLES[v] || 'bg-slate-100 text-slate-600 border-slate-300'
      )}
    >
      {label || v}
    </span>
  );
};

export default StatusBadge;
