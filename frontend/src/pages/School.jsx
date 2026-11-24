import { useEffect,useState } from 'react';
import { Link } from 'react-router-dom';
import { Logo } from '@/components/Logo';
import { api } from '@/services/api';
export default function School(){
 const [rows,setRows]=useState([]),[message,setMessage]=useState('Loading assigned roster…');
 const load=()=>api.get('/privacy/school/roster').then(r=>{setRows(r.data);setMessage('School release changes eligibility only. Student consent remains independent.');}).catch(()=>setMessage('Assigned school sign-in required.'));
 useEffect(()=>{load();},[]);
 async function release(x){try{await api.put(`/privacy/school/${x.id}/release`,{released:!x.academic_released});load();}catch{setMessage('Release failed.');}}
 return <div className="container-page py-8 space-y-6"><Logo/><Link to="/login" className="btn-ghost">Switch account</Link><h1 className="font-display text-2xl font-bold">Assigned school roster</h1><p role="status">{message}</p>{rows.map(x=><article key={x.id} className="card p-5 flex flex-wrap items-center justify-between gap-4"><div><h2 className="font-bold">{x.full_name}</h2><p>{x.university_name} · {x.field_name}</p></div><button className="btn-primary" onClick={()=>release(x)}>{x.academic_released?'Withdraw academic release':'Release academic record'}</button></article>)}</div>;
}
