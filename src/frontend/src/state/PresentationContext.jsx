import { createContext, useContext, useEffect, useState } from 'react';

const defaultForm = {
  ticker: '',
  analysisDate: '',
  selectedAnalysts: [],
  researchRounds: 1,
  riskRounds: 1,
  deepModel: '',
  quickModel: '',
  portfolioMode: 'none', // none | empty | json
  portfolioText: '',
  maxModelRequests: '',
};

const PresentationContext = createContext(null);
const RUN_KEY = 'research-console-run-id';
const rememberedRun = () => {
  try {
    const id = sessionStorage.getItem(RUN_KEY);
    return /^\d{8}T\d{6}Z-[a-f0-9]{8}$/.test(id || '') ? id : null;
  } catch { return null; }
};

export const PresentationProvider = ({ children }) => {
  const [form, setForm] = useState(defaultForm);
  const [prepared, setPrepared] = useState(null); // backend-validated snapshot
  const [confirmed, setConfirmed] = useState(false);
  const [runId, setRunId] = useState(rememberedRun);
  const [activeTab, setActiveTab] = useState(() => rememberedRun() ? 'live' : 'configure');

  useEffect(() => {
    try {
      if (runId) sessionStorage.setItem(RUN_KEY, runId);
      else sessionStorage.removeItem(RUN_KEY);
    } catch { /* History remains available when browser storage is disabled. */ }
  }, [runId]);

  // Any configuration change invalidates the previous backend validation and confirmation.
  const updateForm = (patch) => {
    setForm((f) => ({ ...f, ...patch }));
    setConfirmed(false);
    setPrepared(null);
  };

  return (
    <PresentationContext.Provider
      value={{
        form,
        updateForm,
        prepared,
        setPrepared,
        confirmed,
        setConfirmed,
        runId,
        setRunId,
        activeTab,
        setActiveTab,
      }}
    >
      {children}
    </PresentationContext.Provider>
  );
};

export const usePresentation = () => {
  const ctx = useContext(PresentationContext);
  if (!ctx) throw new Error('usePresentation must be used within PresentationProvider');
  return ctx;
};
