import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/apiClient';
import UnavailableNotice from '@/components/common/UnavailableNotice';
import PreviewDialog from './PreviewDialog';

// Backend-generated file browser: reports, stage reports, sanitized discussion
// records, manifest JSON and sanitized run events — via file IDs/URLs only.
const FileBrowser = ({ runId }) => {
  const { data, isError, error } = useQuery({
    queryKey: ['run-files', runId],
    queryFn: () => api.getFiles(runId),
    enabled: !!runId,
    refetchInterval: 3000,
  });
  const files = data?.files || (Array.isArray(data) ? data : []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Files for run {runId || '—'}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {!runId && <p className="text-sm text-slate-500">No run selected.</p>}
        {isError && <UnavailableNotice message={`File listing unavailable: ${error.message}`} />}
        {runId && data && !files.length && (
          <p className="text-sm text-slate-500">No files reported by the backend for this run.</p>
        )}
        <ul className="divide-y">
          {files.map((f, i) => {
            const id = f.fileId || f.id || f.name;
            const name = f.name || f.filename || id;
            const url = api.fileDownloadUrl(runId, f);
            return (
              <li key={id || i} className="flex flex-wrap items-center justify-between gap-3 py-2">
                <div>
                  <p className="text-sm font-medium">{name}</p>
                  <p className="text-xs text-slate-500">
                    {f.category || 'file'}
                    {f.size != null ? ` · ${f.size} bytes` : ''}
                  </p>
                </div>
                <div className="flex gap-2">
                  <PreviewDialog name={name} url={url} kind={f.kind} />
                  <Button asChild variant="outline" size="sm">
                    <a href={url} download>Download</a>
                  </Button>
                </div>
              </li>
            );
          })}
        </ul>
        <p className="text-xs text-slate-500">
          Previews and downloads use backend-provided file identifiers only — never arbitrary
          filesystem paths.
        </p>
      </CardContent>
    </Card>
  );
};

export default FileBrowser;
