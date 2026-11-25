// Truthful "backend unavailable" state — never substituted with fake results.
const UnavailableNotice = ({ message }) => (
  <div className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900">
    <p className="font-semibold">Backend unavailable</p>
    <p className="mt-0.5 text-xs">{message}</p>
  </div>
);

export default UnavailableNotice;
