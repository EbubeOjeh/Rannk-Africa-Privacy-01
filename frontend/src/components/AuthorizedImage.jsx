import { useEffect,useState } from 'react';
import { api } from '@/services/api';
export default function AuthorizedImage({src,...props}){
 const [url,setUrl]=useState(null);
 useEffect(()=>{let live=true,objectUrl;setUrl(null);if(!src)return;
   if(!src.startsWith('/uploads/')){setUrl(src);return;}
   api.get(src,{baseURL:'',responseType:'blob'}).then(r=>{objectUrl=URL.createObjectURL(r.data);if(live)setUrl(objectUrl);else URL.revokeObjectURL(objectUrl);}).catch(()=>{});
   return()=>{live=false;if(objectUrl)URL.revokeObjectURL(objectUrl);};
 },[src]);
 return url?<img src={url} {...props}/>:null;
}
