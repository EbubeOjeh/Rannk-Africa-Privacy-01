import AuthorizedImage from '@/components/AuthorizedImage';
import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Link } from 'react-router-dom';

function Preview({ value }) {
  if (!value) return <p className="text-cream/60">Not discoverable under the saved settings and current release checks.</p>;
  return <div className="space-y-2">
    {value.avatar_url && <AuthorizedImage src={value.avatar_url} alt="Shared profile" className="w-16 h-16 rounded-full" />}
    <p className="font-bold">{value.full_name}</p><p>{value.university_name} · {value.field_name}</p>
    <p>Illustrative score: {value.final_score}/100</p>
    {value.bio && <p>{value.bio}</p>}
    {value.portfolio_url && <a href={value.portfolio_url} target="_blank" rel="noreferrer" className="text-gold-300 underline">Portfolio</a>}
    <p className="text-xs text-cream/50">Email, phone, CV and transcript are excluded from discovery.</p>
  </div>;
}
export default function Privacy() {
  const [saved,setSaved]=useState(null),[draft,setDraft]=useState(null),[history,setHistory]=useState([]);
  const [message,setMessage]=useState(''),[busy,setBusy]=useState(false);
  const loadHistory=()=>api.get('/privacy/history').then(r=>setHistory(r.data));
  useEffect(()=>{api.get('/privacy/me').then(r=>{setSaved(r.data);setDraft(r.data.choices);}).catch(()=>setMessage('Could not load privacy settings.'));loadHistory().catch(()=>{});},[]);
  const dirty=saved && JSON.stringify(saved.choices)!==JSON.stringify(draft);
  async function save(choices=draft){
    setBusy(true);setMessage('Saving…');
    try {const r=await api.put('/privacy/me',choices);setSaved(r.data);setDraft(r.data.choices);setMessage('Settings saved. Previews below show the saved response.');await loadHistory();}
    catch {setMessage('Save failed. Your last saved settings still apply.');} finally {setBusy(false);}
  }
  if(!saved)return <p role="status">{message || 'Loading privacy settings…'}</p>;
  return <div className="space-y-6">
    <div><h1 className="font-display text-2xl font-bold">Privacy and sharing</h1><p className="mt-3 text-cream/75">{saved.notice}</p></div>
    <p className="card p-4 text-sm">{saved.retention}</p>
    <p className="text-sm text-cream/60">School academic release: {saved.academic_released?'eligible':'not released'}. Release never changes your consent.</p>
    <form onSubmit={e=>{e.preventDefault();save();}} className="space-y-5">
      <div className="grid md:grid-cols-2 gap-5">{['public','recruiter'].map(a=><fieldset key={a} className="card p-5 space-y-4">
        <legend className="font-bold px-2 capitalize">{a==='public'?'Public visitors':'Approved recruiters'}</legend>
        <p className="text-sm text-cream/65">Participation shares your name, university, field and illustrative score.</p>
        {['enabled','bio','photo','portfolio'].map(f=><label key={f} className="flex items-center gap-3">
          <input type="checkbox" className="accent-yellow-500 w-4 h-4" checked={draft[a+'_'+f]} disabled={busy || (f!=='enabled'&&!draft[a+'_enabled'])}
            onChange={e=>{const next={...draft,[a+'_'+f]:e.target.checked};if(f==='enabled'&&!e.target.checked){for(const x of ['bio','photo','portfolio'])next[a+'_'+x]=false;}setDraft(next);}} />
          <span>{f==='enabled'?'Join this discovery audience':`Share ${f==='bio'?'biography':f==='photo'?'photo':'portfolio link'} (optional)`}</span>
        </label>)}
      </fieldset>)}</div>
      <div role="status" aria-live="polite" className="text-gold-300">{dirty?'Unsaved changes. Current disclosure and previews still use your last saved settings.':message || 'Showing saved settings.'}</div>
      <div className="flex flex-wrap gap-3"><button className="btn-primary" disabled={busy || !dirty}>Save privacy settings</button>
        <button type="button" className="btn-ghost" disabled={busy} onClick={()=>save(Object.fromEntries(Object.keys(draft).map(k=>[k,false])))}>Withdraw from both audiences</button>
        <Link className="btn-ghost" to="/opportunities">Browse opportunities</Link></div>
    </form>
    <h2 className="font-display text-xl font-bold">Saved audience previews</h2>
    <div className="grid md:grid-cols-2 gap-5">{['public','recruiter'].map(a=><section className="card p-5" key={a}><h3 className="capitalize font-bold mb-3">{a} preview</h3><Preview value={saved.previews[a]} /></section>)}</div>
    <section className="card p-5"><h2 className="font-bold mb-4">Your sharing history</h2>{history.length===0?<p>No saved choices or applications yet.</p>:<ul className="space-y-3">{history.map((x,i)=><li key={i} className="text-sm"><strong>{x.action}</strong> · {new Date(x.created_at).toLocaleString()}<pre className="whitespace-pre-wrap break-words text-cream/60 text-xs mt-1">{JSON.stringify(x.details,null,2)}</pre></li>)}</ul>}</section>
  </div>;
}
