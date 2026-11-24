import { useEffect,useRef,useState } from 'react';
import { api } from '@/services/api';
export default function ApplicationReview({review,onClose,onSubmitted}){
 const [choices,setChoices]=useState({email:false,bio:false,photo:false,portfolio:false});
 const [confirmed,setConfirmed]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const dialog=useRef(null);
 useEffect(()=>{const el=dialog.current;el.showModal();return()=>{el.close();};},[]);
 async function submit(e){e.preventDefault();setBusy(true);setError('');try{const r=await api.post(`/opportunities/${review.opportunity_id}/apply`,{...choices,confirmed,recipient_id:review.recipient_id});onSubmitted(r.data);}catch(err){setError(err.response?.data?.detail || err.response?.data?.error?.message || 'Submission failed. Please review again.');setBusy(false);}}
 return <dialog ref={dialog} onCancel={e=>{e.preventDefault();if(!busy)onClose();}} className="card text-cream bg-ink-950 w-full max-w-xl p-6 max-h-[90vh] overflow-y-auto backdrop:bg-black/80">
 <form onSubmit={submit} className="space-y-4"><h2 className="font-display text-xl font-bold">Review application</h2><p>{review.title}</p><p><strong>Recipient: {review.recipient_name}</strong></p>
 <p>Required fields: name, university, field and illustrative score. Applying does not enable discovery.</p><div className="bg-white/5 p-3 rounded-lg text-sm">{review.required.full_name} · {review.required.university_name} · {review.required.field_name} · {review.required.final_score}/100</div>
 <fieldset className="space-y-3"><legend className="font-bold mb-3">Optional information for this application only</legend>{Object.keys(choices).map(k=><label key={k} className="flex gap-3 items-center"><input type="checkbox" checked={choices[k]} disabled={busy} onChange={e=>setChoices({...choices,[k]:e.target.checked})}/><span>Share {k==='bio'?'biography':k==='portfolio'?'portfolio link':k}</span></label>)}</fieldset>
 <p className="text-sm text-cream/70">{review.retention}</p><label className="flex gap-3"><input type="checkbox" required checked={confirmed} disabled={busy} onChange={e=>setConfirmed(e.target.checked)}/><span>I confirm sharing the required fields and my selected extras with {review.recipient_name}.</span></label>
 <p role="alert" className="text-red-300">{error}</p><div className="flex gap-3"><button type="button" className="btn-ghost" disabled={busy} onClick={onClose}>Cancel without applying</button><button className="btn-primary" disabled={!confirmed||busy}>{busy?'Sending…':'Send application'}</button></div></form></dialog>;
}
