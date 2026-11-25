import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Settings } from 'lucide-react';
import { getBaseUrl, setBaseUrl } from '@/lib/apiClient';

// Configurable API base URL, preferably same-origin /api.
// No API keys or model-server credentials can be entered here by design.
const ApiSettings = () => {
  const [value, setValue] = useState(getBaseUrl());
  const queryClient = useQueryClient();

  const save = () => {
    setBaseUrl(value);
    queryClient.invalidateQueries();
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-1">
          <Settings size={14} /> API settings
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Backend API base URL</DialogTitle>
        </DialogHeader>
        <Input value={value} onChange={(e) => setValue(e.target.value)} placeholder="/api" />
        <p className="text-xs text-slate-500">
          Prefer the same-origin path /api. This frontend never requests, stores or transmits
          API keys, and there is no arbitrary model-server URL field.
        </p>
        <Button onClick={save} className="bg-emerald-600 hover:bg-emerald-700">
          Save and reload backend data
        </Button>
      </DialogContent>
    </Dialog>
  );
};

export default ApiSettings;
