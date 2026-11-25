import MarkdownView from '@/components/common/MarkdownView';

// Renders messages exactly as supplied by the backend. Agent labels, sequence,
// timestamps and round numbers appear only when the backend provides them.
const DiscussionStream = ({ messages }) => {
  if (!messages.length) {
    return <p className="py-4 text-sm text-slate-500">No messages in this view yet.</p>;
  }
  return (
    <div className="space-y-3">
      {messages.map((m, i) => (
        <div key={m.id || i} className="rounded-md border bg-white p-3">
          <div className="mb-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
            {m.sequence != null && <span className="font-mono">#{m.sequence}</span>}
            <span className="font-semibold text-emerald-700">{m.agent || m.agentLabel || 'Agent'}</span>
            {m.round != null && <span>Round {m.round}</span>}
            {m.timestamp && <span>{m.timestamp}</span>}
          </div>
          <MarkdownView content={m.content || m.message || ''} />
        </div>
      ))}
    </div>
  );
};

export default DiscussionStream;
