import { useEffect,useState } from 'react';
import { api } from '@/services/api';
export default function Applications(){
 const [rows,setRows]=useState([]),[message,setMessage]=useState('Loading applications…');
 useEffect(()=>{api.get('/privacy/applications').then(r=>{setRows(r.data);setMessage(r.data.length?'':'No applications shared with this account.');}).catch(()=>setMessage('Applications unavailable. Recipient approval is checked on every request.'));},[]);
 return <div className="space-y-5"><h1 className="font-display text-2xl font-bold">Shared applications</h1><p className="text-cream/65">Each application contains the fields authorized when it was sent. Discovery withdrawal does not remove it. Applications are retained until the demonstration database is reset.</p><p role="status">{message}</p>{rows.map(x=><article key={x.id} className="card p-5 space-y-2"><h2 className="font-bold">{x.snapshot.full_name}</h2><p>Recipient: {x.recipient_name}</p><p className="text-xs text-cream/50">{new Date(x.created_at).toLocaleString()}</p><dl className="space-y-2">{Object.entries(x.snapshot).filter(([k])=>!['id','university_id','field_id'].includes(k)).map(([k,v])=><div key={k}><dt className="text-xs uppercase text-cream/50">{k.replaceAll('_',' ')}</dt><dd className="break-words">{v??'Not provided'}</dd></div>)}</dl></article>)}</div>;
}
