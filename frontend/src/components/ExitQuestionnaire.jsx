import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/services/api';

export default function ExitQuestionnaire() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false), [config, setConfig] = useState(null);
  const [name, setName] = useState(''), [studentId, setStudentId] = useState('');
  const [answers, setAnswers] = useState(Array(7).fill(null)), [review, setReview] = useState('');
  const [consent, setConsent] = useState(false), [busy, setBusy] = useState(false), [message, setMessage] = useState('');
  const dialog = useRef(null), previousFocus = useRef(null);
  useEffect(() => { setOpen(false); setName(''); setStudentId(''); setAnswers(Array(7).fill(null)); setReview(''); setConsent(false); setConfig(null); setMessage(''); }, [user?.id]);
  function finish() { setOpen(false); logout(); navigate('/', { replace: true }); }
  function close() { setOpen(false); previousFocus.current?.focus(); }
  useEffect(() => {
    async function request() {
      previousFocus.current = document.activeElement;
      setOpen(true); setConfig(null); setMessage('Loading the optional exit review…');
      try {
        const status = await api.get('/classroom/exit-feedback/me');
        if (status.data.submitted) { finish(); return; }
        const response = await api.get('/classroom/exit-questionnaire');
        setConfig(response.data); setName(response.data.registered_name || ''); setStudentId(response.data.student_identifier || ''); setMessage('');
      } catch { setMessage('The review could not load. You can still log out without submitting.'); }
    }
    window.addEventListener('rankafrica:student-logout', request);
    return () => window.removeEventListener('rankafrica:student-logout', request);
  }, [user?.id]);
  useEffect(() => {
    if (!open) return;
    const old = document.body.style.overflow; document.body.style.overflow = 'hidden';
    dialog.current?.querySelector('button')?.focus();
    return () => { document.body.style.overflow = old; };
  }, [open]);
  function keys(e) {
    if (e.key === 'Escape' && !busy) { e.preventDefault(); close(); }
    if (e.key !== 'Tab') return;
    const nodes = [...dialog.current.querySelectorAll('button:not(:disabled),input:not(:disabled),textarea:not(:disabled),a[href]')];
    const first = nodes[0], last = nodes.at(-1);
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
    if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
  }
  async function submit(e) {
    e.preventDefault(); setBusy(true); setMessage('Saving your response…');
    try {
      const r = await api.post('/classroom/exit-feedback/me', { respondent_name: name, student_identifier: studentId, answers, general_review: review, consent_to_submit: consent });
      const suffix = r.data.email_status === 'sent' ? 'The email server accepted your response for delivery.' : 'Your response is safely saved. Email delivery is pending facilitator configuration or retry.';
      setMessage('Thank you. ' + suffix); setConfig(c => ({ ...c, submitted: true }));
    } catch (err) { setMessage(typeof err.response?.data?.detail === 'string' ? err.response.data.detail : 'Could not save. Try again, or log out without submitting.'); }
    finally { setBusy(false); }
  }
  if (!open || !user) return null;
  return <div className="fixed inset-0 z-[100] bg-black/75 flex items-center justify-center p-3 sm:p-6">
    <section ref={dialog} role="dialog" aria-modal="true" aria-labelledby="exit-review-title" onKeyDown={keys} className="card bg-ink-950 w-full max-w-2xl max-h-[90dvh] overflow-y-auto p-5 sm:p-7 space-y-5">
      <div className="flex justify-between items-start gap-4"><h2 id="exit-review-title" className="font-display text-2xl font-bold">Before you log out</h2><button type="button" className="btn-ghost" disabled={busy} onClick={close} aria-label="Close review and stay signed in">Close</button></div>
      <p className="text-sm text-cream/75">Please give a brief privacy review. Participation is optional. Your name, student ID and answers are visible only to the facilitator and are not added to public rankings or recruiter profiles.</p>
      {config && !config.submitted && <><p className="text-sm text-cream/70">Email recipient: {config.recipient || 'Not configured yet; your response can be saved for the facilitator.'}<br/>Contact: {config.contact || 'Ask your facilitator'}<br/>Retention: {config.retention || 'Ask your facilitator before submitting identifying information.'}</p>
      {!config.email_configured && <p className="text-sm text-gold-300">Email delivery is not configured. Responses will be saved privately for administrator review.</p>}
      <form onSubmit={submit} className="space-y-5">
        <label className="block"><span className="field-label">Your name</span><input className="input w-full" value={name} onChange={e => setName(e.target.value)} maxLength={180} autoComplete="name" required /></label>
        <label className="block"><span className="field-label">Student ID</span><input className="input w-full" value={studentId} onChange={e => setStudentId(e.target.value)} maxLength={100} required /></label>
        <p className="text-sm text-cream/65">For ratings: 1 = very unlikely and 5 = very likely. You may leave questions unanswered.</p>
        {config.questions.map((q, i) => <fieldset key={i} className="border border-white/10 rounded-xl p-4 space-y-2"><legend className="px-2 font-medium">{i + 1}. {q.question}</legend>{q.options.map(option => <label className="flex items-start gap-3 py-2 min-h-[44px]" key={option}><input className="mt-1" type="radio" name={'exit-q-' + i} checked={answers[i] === option} onChange={() => setAnswers(a => a.map((v, j) => j === i ? option : v))} /><span>{option}</span></label>)}<button type="button" className="text-sm text-gold-300 underline" onClick={() => setAnswers(a => a.map((v, j) => j === i ? null : v))}>Leave unanswered</button></fieldset>)}
        <label className="block"><span className="field-label">General comment</span><span className="block text-sm text-cream/65 mb-2">How easy were the privacy choices to understand and use? Did starting with your profile hidden meet your expectations? What should improve?</span><textarea className="input w-full min-h-[120px]" value={review} onChange={e => setReview(e.target.value)} maxLength={3000} placeholder="Optional: share your experience in a few sentences." /></label>
        <label className="flex items-start gap-3"><input className="mt-1" type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} required /><span className="text-sm">{config.consent_text}</span></label>
        <button type="submit" className="btn-primary" disabled={busy || !consent}>{busy ? 'Saving…' : 'Submit review'}</button>
      </form></>}
      <p role="status" aria-live="polite" className="text-sm">{message}</p>
      <div className="flex flex-wrap gap-3"><button type="button" className="btn-ghost" disabled={busy} onClick={finish}>{config?.submitted ? 'Finish logging out' : 'Log out without submitting'}</button><button type="button" className="btn-ghost" disabled={busy} onClick={close}>Stay signed in</button></div>
    </section>
  </div>;
}
