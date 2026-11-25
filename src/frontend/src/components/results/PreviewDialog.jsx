import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import MarkdownView from '@/components/common/MarkdownView';

// Preview uses the backend-provided download URL only. HTML reports are shown in
// a sandboxed iframe without script execution; everything else renders as Markdown.
const PreviewDialog = ({ name, url, kind }) => {
  const [content, setContent] = useState(null);
  const [error, setError] = useState(null);
  const isHtml = kind === 'html' || /\.html?$/i.test(name || '');

  const load = async () => {
    setContent(null);
    setError(null);
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Preview failed with status ${res.status}`);
      setContent(await res.text());
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" onClick={load}>Preview</Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="truncate pr-6 text-base">{name}</DialogTitle>
        </DialogHeader>
        {error && <p className="text-sm text-red-600">{error}</p>}
        {!error && content == null && <p className="text-sm text-slate-500">Loading preview…</p>}
        {content != null && isHtml && (
          <iframe
            title={name}
            sandbox=""
            srcDoc={content}
            className="h-[60vh] w-full rounded border bg-white"
          />
        )}
        {content != null && !isHtml && kind === 'json' && <pre className="max-h-[65vh] overflow-auto whitespace-pre-wrap break-words rounded bg-slate-50 p-4 text-xs">{content}</pre>}
        {content != null && !isHtml && kind !== 'json' && <MarkdownView content={content} />}
      </DialogContent>
    </Dialog>
  );
};

export default PreviewDialog;
