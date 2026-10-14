import {NextResponse} from 'next/server';
import {GET as sessionStatus} from '../auth/route';
const headers={'Cache-Control':'no-store'};
const endpoint='https://api.ucii.sportgen-ai.com/alexa/auth/authority';
export async function POST(request:Request){
 if(request.headers.get('origin')!==new URL(request.url).origin)return NextResponse.json({message:'Request origin rejected.'},{status:403,headers});
 let body:any;
 try{
  const raw=await request.text();if(raw.length>4096)throw new Error();body=JSON.parse(raw);
  if(!body||typeof body!=='object'||Array.isArray(body))throw new Error();
  if(body.command==='grant'){
   if(Object.keys(body).sort().join(',')!=='command,confirmation,operation'||body.confirmation!=='GRANT_OPERATION_AUTHORITY'||typeof body.operation!=='string'||! /^[A-Za-z][A-Za-z0-9_.:-]{0,127}$/.test(body.operation))throw new Error();
  }else if(body.command==='revoke'){
   if(Object.keys(body).sort().join(',')!=='authority_id,command,confirmation'||body.confirmation!=='REVOKE_OPERATION_AUTHORITY'||typeof body.authority_id!=='string'||! /^[0-9a-f-]{36}$/i.test(body.authority_id))throw new Error();
  }else throw new Error();
 }catch{return NextResponse.json({message:'Review one exact authority change.'},{status:400,headers});}
 const status=await sessionStatus(request);
 const session=await status.json() as {authentication?:string;identity_id?:string};
 if(!status.ok)return NextResponse.json({message:'HUMAN session check unavailable.'},{status:503,headers});
 if(session.authentication!=='AUTHENTICATED')return NextResponse.json({message:'Sign in with UCII before approving authority.'},{status:401,headers});
 const handle=request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-ucii-session='))?.slice('__Host-ucii-session='.length)||'';
 if(! /^[A-Za-z0-9_-]{43}$/.test(handle))return NextResponse.json({message:'Sign in with UCII before approving authority.'},{status:401,headers});
 try{
  const response=await fetch(endpoint,{method:'POST',redirect:'manual',signal:AbortSignal.timeout(42000),headers:{'Content-Type':'application/json',Authorization:'Bearer '+handle},body:JSON.stringify(body)});
  const data=await response.json() as any;
  if(!response.ok)return NextResponse.json({message:response.status===403?'A matching, unused operator authorization is required. No successful authority change confirmed.':response.status===401?'Sign in again before approving authority.':'Authority change outcome uncertain. Check authority before retrying.'},{status:[401,403].includes(response.status)?response.status:503,headers});
  if(typeof data.authority_id!=='string'||! /^[0-9a-f-]{36}$/i.test(data.authority_id)||typeof data.identity_id!=='string'||(body.command==='grant'?(!Array.isArray(data.allowed_operations)||!data.allowed_operations.every((x:unknown)=>typeof x==='string')||data.status!=='granted'||data.authority_state!=='ACTIVE'||data.allowed_operations.length!==1||data.allowed_operations[0]!==body.operation||data.granted_by!==session.identity_id):(data.status!=='revoked'||data.authority_state!=='REVOKED'||data.authority_id!==body.authority_id)))throw new Error();
  return NextResponse.json({authority:{authority_id:data.authority_id,identity_id:data.identity_id,authority_state:data.authority_state,allowed_operations:data.allowed_operations},message:body.command==='grant'?'UCII granted standing operation authority. Check authority again; execution remains blocked.':'UCII revoked this authority record. Check authority again.'},{headers});
 }catch{return NextResponse.json({message:'Authority change outcome uncertain. Check authority before retrying.'},{status:503,headers});}
}
