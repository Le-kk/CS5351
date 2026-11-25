'use strict';
const $ = id => document.getElementById(id);
const number = value => value == null ? '—' : new Intl.NumberFormat('en-US', {maximumFractionDigits: 1}).format(value);
let bootstrap, current = null, timer = null, fileText = null, fileName = null;

async function api(path, payload) {
  const options = payload === undefined ? {} : {method: 'POST', headers: {
    'Content-Type': 'application/json', 'X-Demo-Token': bootstrap.csrf_token}, body: JSON.stringify(payload)};
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) {
    const error = new Error(data.error || 'The request could not be completed.');
    error.details = data;
    throw error;
  }
  return data;
}
function mode() { return document.querySelector('input[name="portfolio"]:checked').value; }
function toast(message) { $('toast').textContent = message; $('toast').hidden = false; setTimeout(() => $('toast').hidden = true, 3500); }
function showError(error) {
  const detail = error.details || {};
  $('inputError').textContent = [detail.kind, error.message, detail.field ? `Field: ${detail.field}` : '',
    detail.model_dispatches === 0 ? 'Blocked before execution · 0 model dispatches.' : ''].filter(Boolean).join(' ');
  $('inputError').hidden = false;
}
function resetView() {
  if (timer) clearTimeout(timer);
  timer = null;
  $('reportReady').hidden = true; $('reportEmpty').hidden = false; $('resultBar').hidden = true;
  $('reportFrame').removeAttribute('src'); $('downloadManifest').hidden = true;
  $('callMetric').textContent = '—'; $('inputMetric').textContent = '—'; $('outputMetric').textContent = '—';
  $('timeMetric').textContent = '—'; $('evidenceJson').textContent = 'No published artifacts for this input.';
  $('eventLog').replaceChildren(); $('progressStrip').replaceChildren();
}
function invalidate() {
  $('inputError').hidden = true;
  $('consent').checked = false; $('runButton').disabled = true; $('confirmation').hidden = true;
  if (current && current.state === 'FROZEN') {
    const id = current.run_id; current = null;
    api('/api/cancel', {run_id: id}).catch(() => {});
  }
  updatePreview();
}
function updatePreview() {
  const selected = mode();
  $('uploadArea').hidden = selected !== 'custom';
  $('portfolioPreview').textContent = selected === 'none' ? 'No portfolio file. Holdings and cash remain unknown.' :
    selected === 'custom' ? (fileText || 'Choose a JSON file to inspect it.') : JSON.stringify(bootstrap.samples[selected], null, 2);
}
function configureExecution() {
  const live = $('execution').value === 'live';
  $('modeExplanation').textContent = live ? 'Real configured model and vendor calls. API costs may apply. Inputs can be transmitted to providers only after confirmation.' :
    'Synthetic analyst responses. Real input checks, immutable context, report publication and call-budget enforcement. No remote model requests.';
  for (const option of $('scenario').options) option.disabled = live && !['normal', 'budget'].includes(option.value);
  if ($('scenario').selectedOptions[0].disabled) $('scenario').value = 'normal';
  invalidate();
}
function frozenSummary(job) {
  const rows = [['Instrument', job.input.ticker], ['Analysis date', job.input.analysis_date],
    ['Input mode', job.input.input_mode], ['Portfolio file', job.input.basename || 'Not supplied'],
    ['Execution', job.mode === 'scripted' ? 'Scripted · no remote model' : 'Live · configured provider'],
    ['Call limit', job.call_cap == null ? 'No cap' : job.call_cap]];
  const dl = document.createElement('dl');
  for (const [label, value] of rows) {
    const dt = document.createElement('dt'), dd = document.createElement('dd');
    dt.textContent = label; dd.textContent = value; dl.append(dt, dd);
  }
  $('frozenSummary').replaceChildren(dl);
  $('fingerprint').textContent = job.input.fingerprint_sha256 ? `Frozen SHA-256: ${job.input.fingerprint_sha256}` : 'No portfolio snapshot: holdings and cash are unknown.';
  $('consentText').textContent = job.mode === 'scripted' ? 'I confirm these frozen demo inputs. No remote model will be contacted.' :
    'I confirm these frozen inputs and authorize real API calls. Holdings may be sent to the configured model provider; API costs can apply.';
}
async function prepare(overrideMode) {
  invalidate(); resetView(); current = null;
  if (mode() === 'custom' && !fileText && !overrideMode) throw new Error('Choose a JSON portfolio file first.');
  const cap = $('callCap').value;
  const job = await api('/api/prepare', {ticker: $('ticker').value, analysis_date: $('analysisDate').value,
    execution: $('execution').value, portfolio_mode: overrideMode || mode(),
    portfolio_json: fileText, filename: fileName || 'demo-portfolio.json',
    scenario: $('scenario').value, call_cap: cap === '' ? null : Number(cap)});
  current = job; paint(job); frozenSummary(job);
  $('confirmation').hidden = false;
}
function lockForm(locked) {
  document.querySelectorAll('#setupForm input, #setupForm select, #setupForm button, #execution').forEach(el => el.disabled = locked);
  $('cancelButton').disabled = locked;
}
function paint(job) {
  const result = job.result;
  const scripted = job.mode === 'scripted';
  $('runHeading').textContent = job.state === 'RUNNING' ? 'Following the research run.' :
    job.state === 'FROZEN' ? 'Inputs frozen. Your confirmation next.' :
    job.state === 'CANCELLED' ? 'Cancelled before execution.' :
    job.state === 'ERROR' ? 'A report was not published.' :
    result?.run_outcome === 'INCOMPLETE' ? 'Stopped with a clear reason.' :
    result?.output_check === 'NEEDS_REVIEW' ? 'Published for human review.' : 'A report, with its evidence.';
  $('runBadge').textContent = result ? result.run_outcome : job.state;
  $('runBadge').className = 'badge ' + (result?.run_outcome === 'INCOMPLETE' || job.state === 'ERROR' ? 'danger' :
    result?.output_check === 'NEEDS_REVIEW' ? 'warning' : job.state === 'FINISHED' ? 'success' : 'neutral');
  $('runDescription').textContent = scripted ? 'Scripted analysis through the real application boundary. No market evidence or financial quality is measured here.' :
    'Actual graph and configured providers. Usage below is observed provider usage; missing usage is never treated as zero.';
  $('callMetricLabel').textContent = scripted ? 'Local SDK dispatches' : (job.budget ? 'Transport dispatches' : 'Model invocations observed');
  $('callMetric').textContent = number(job.calls);
  $('capMetric').textContent = job.call_cap == null ? 'Call cap disabled' : `Limit: ${job.call_cap} · not a token ceiling`;
  $('inputMetric').textContent = number(job.tokens_in); $('outputMetric').textContent = number(job.tokens_out);
  $('timeMetric').textContent = `${number(job.elapsed)}s`; $('phaseMetric').textContent = job.stage;
  const usage = scripted ? 'Synthetic fixture usage' : job.tokens_in == null ? 'Provider usage not yet available' :
    job.usage_complete ? 'Provider-reported usage observed' : 'Partial provider usage';
  document.querySelectorAll('.usage-label').forEach(el => el.textContent = usage);
  $('usageNotice').textContent = scripted ? 'Scripted token counts are illustrative fixture usage, not an efficiency measurement. Historical results are shown separately below.' :
    'This run has no matched unoptimized control. Do not infer a percentage reduction from its token count alone. Observed usage may be incomplete.';
  const progress = document.createDocumentFragment();
  if (scripted) bootstrap.stages.forEach((stage, index) => {
    const span = document.createElement('span');
    const isDone = index < job.calls;
    const isStopped = result?.run_outcome === 'INCOMPLETE' && index === job.calls;
    span.className = isDone ? 'done' : isStopped ? 'stopped' : job.state === 'RUNNING' && index === job.calls ? 'active' : '';
    span.textContent = stage.replace(' analysis', '').replace(' discussion', '').replace(' plan', '');
    span.title = `Scripted stage ${index + 1}: ${stage}`; progress.append(span);
  });
  else { const span = document.createElement('span'); span.className = job.state === 'RUNNING' ? 'active' : '';
    span.textContent = job.stage; progress.append(span); }
  $('progressStrip').replaceChildren(progress);
  const log = document.createDocumentFragment();
  for (const entry of job.events) { const li = document.createElement('li');
    const t = document.createElement('time'); t.textContent = `${entry.time.toFixed(2)}s`;
    const text = document.createElement('span'); text.textContent = entry.message; li.append(t, text); log.append(li); }
  $('eventLog').replaceChildren(log);
  $('evidenceJson').textContent = JSON.stringify({input: job.input, execution: job.mode,
    usage_kind: job.usage_kind, observed_usage_complete: job.usage_complete,
    call_budget: job.budget, result: job.result}, null, 2);
  const total = job.tokens_in == null ? null : job.tokens_in + job.tokens_out;
  if (total != null) $('usageNotice').textContent = `${scripted ? 'Synthetic fixture total' : 'Observed usage total'}: ${number(total)} tokens. ` + $('usageNotice').textContent;
  if (result) {
    $('resultBar').hidden = false;
    $('resultBar').className = 'result-bar ' + (result.run_outcome === 'INCOMPLETE' ? 'result-incomplete' : result.output_check === 'NEEDS_REVIEW' ? 'result-review' : '');
    $('ratingResult').textContent = result.final_rating || 'Not assigned';
    $('checkResult').textContent = result.output_check;
    $('stopResult').textContent = result.stop_reason || 'None';
  }
  if (job.artifact_ready) {
    const base = `/api/runs/${encodeURIComponent(job.run_id)}/`;
    $('reportEmpty').hidden = true; $('reportReady').hidden = false;
    if ($('reportFrame').getAttribute('src') !== base + 'html') $('reportFrame').src = base + 'html';
    $('openReport').href = base + 'html'; $('downloadMarkdown').href = base + 'markdown';
    $('downloadManifest').href = base + 'manifest'; $('downloadManifest').hidden = false;
  }
}
async function poll() {
  if (!current || current.state !== 'RUNNING') return;
  try {
    current = await api(`/api/runs/${encodeURIComponent(current.run_id)}`); paint(current);
    if (current.state === 'RUNNING') timer = setTimeout(poll, 400);
    else { lockForm(false); $('runButton').disabled = true; $('confirmation').hidden = true; }
  } catch (error) {
    // A browser/network error is not a completed or failed model verdict.
    $('runBadge').textContent = 'CONNECTION LOST';
    $('runDescription').textContent = 'The run may still be active. Retrying the status connection; no outcome is inferred.';
    timer = setTimeout(poll, 1500);
  }
}
function renderHistory(h) {
  $('historyBefore').textContent = number(h.before); $('historyAfter').textContent = number(h.after);
  $('historyReduction').textContent = `${h.reduction.toFixed(2)}%`;
  $('beforeBar').style.width = '100%'; $('afterBar').style.width = `${100 * h.after / h.before}%`;
  $('historySource').textContent = `${h.case.ticker} · ${h.case.analysis_date} · ${h.date} measurement · ${h.control_samples} control / ${h.optimized_samples} optimized runs. Source: checked-in provider-usage evidence.`;
  const p = document.createElement('p');
  p.textContent = `Model: ${h.model}. Four analysts; one research and one risk round; isolated empty memory; checkpoints off. Source file: ${h.source}.`;
  const ul = document.createElement('ul');
  for (const limit of h.limitations) { const li = document.createElement('li'); li.textContent = limit; ul.append(li); }
  $('historyDetails').replaceChildren(p, ul);
}
async function init() {
  try {
    bootstrap = await api('/api/bootstrap'); renderHistory(bootstrap.history);
    $('analysisDate').max = new Date().toISOString().slice(0, 10);
    const live = $('execution').querySelector('[value="live"]');
    live.disabled = !bootstrap.allow_live; live.textContent = bootstrap.allow_live ? 'Live analysis · real API calls' : 'Live analysis · enable on launch';
    updatePreview();
  } catch (error) { $('runHeading').textContent = 'The demo service is unavailable.'; showError(error); $('prepareButton').disabled = true; return; }
  $('setupForm').addEventListener('submit', async event => { event.preventDefault(); try { await prepare(); } catch (error) { showError(error); } });
  $('invalidButton').addEventListener('click', async () => {
    try { await prepare('invalid'); }
    catch (error) { showError(error); $('runHeading').textContent = 'Invalid input stopped at the boundary.';
      $('runBadge').textContent = 'INPUT REJECTED'; $('runBadge').className = 'badge danger';
      $('callMetric').textContent = '0'; $('capMetric').textContent = 'No execution was started';
      $('runDescription').textContent = 'The actual input validator rejected a missing quantity before any model dispatch.'; }
  });
  $('setupForm').addEventListener('change', invalidate);
  $('ticker').addEventListener('input', invalidate); $('callCap').addEventListener('input', invalidate);
  $('scenario').addEventListener('change', () => { if ($('scenario').value === 'budget') $('callCap').value = '2'; invalidate(); });
  $('execution').addEventListener('change', configureExecution);
  $('portfolioFile').addEventListener('change', async event => {
    const file = event.target.files[0]; fileText = null; fileName = null;
    if (file) { if (file.size > 32768) { showError(new Error('Choose a JSON file smaller than 32 KB.')); return; }
      fileText = await file.text(); fileName = file.name; }
    invalidate();
  });
  $('consent').addEventListener('change', () => $('runButton').disabled = !$('consent').checked || !current || current.state !== 'FROZEN');
  $('runButton').addEventListener('click', async () => {
    if (!current || !$('consent').checked) return;
    $('runButton').disabled = true;
    try {
      current = await api('/api/start', {run_id: current.run_id, consent: true});
      lockForm(current.state === 'RUNNING'); paint(current);
      if (current.state === 'RUNNING') poll();
      else { $('confirmation').hidden = true; $('runButton').disabled = true; }
    }
    catch (error) { lockForm(false); showError(error); $('runButton').disabled = false; }
  });
  $('cancelButton').addEventListener('click', async () => {
    try { if (current) { current = await api('/api/cancel', {run_id: current.run_id}); paint(current); }
      $('confirmation').hidden = true; toast('Cancelled before any model dispatch.'); } catch (error) { showError(error); }
  });
  document.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-tab]').forEach(tab => { const active = tab === button;
      tab.setAttribute('aria-selected', String(active)); $(`${tab.dataset.tab}Panel`).hidden = !active; });
  }));
  $('notesButton').addEventListener('click', () => { $('presenterNotes').hidden = !$('presenterNotes').hidden;
    if (!$('presenterNotes').hidden) $('presenterNotes').scrollIntoView({behavior: 'smooth'}); });
  $('historyExpand').addEventListener('click', () => $('historyContext').open = true);
}
init();
