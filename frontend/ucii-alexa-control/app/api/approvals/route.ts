import {NextResponse} from 'next/server';
const endpoint='https://api.ucii.sportgen-ai.com/alexa/auth/approvals';
const headers={'Cache-Control':'no-store'};
const uuid=/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/;
async function call(request:Request){
 if(request.method!=='GET'&&request.headers.get('origin')!==new URL(request.url).origin)return NextResponse.json({message:'Request origin rejected.'},{status:403,headers});
 const handle=request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-ucii-session='))?.slice('__Host-ucii-session='.length)||'';
 if(!/^[A-Za-z0-9_-]{43}$/.test(handle))return NextResponse.json({message:'Sign in with UCII first.'},{status:401,headers});
 let body:any,id:string,suffix='';
 try{
  if(request.method!=='GET'){
   const raw=await request.text();if(raw.length>4096)throw new Error();body=JSON.parse(raw);
   if(Object.keys(body).sort().join(',')!=='action_digest,confirmation,proposal_id'||body.confirmation!==(request.method==='DELETE'?'REVOKE_EXACT_APPROVAL':'APPROVE_EXACT_ACTION_ONCE')||!/^sha256:[a-f0-9]{64}$/.test(body.action_digest))throw new Error();
   id=body.proposal_id;
  }else{id=new URL(request.url).searchParams.get('proposal_id')||'';suffix='?proposal_id='+id;}
  if(!uuid.test(id))throw new Error();
 }catch{return NextResponse.json({message:'Confirm one saved exact proposal.'},{status:400,headers});}
 try{
  const upstream=await fetch(endpoint+suffix,{method:request.method,redirect:'manual',signal:AbortSignal.timeout(40000),headers:{Authorization:'Bearer '+handle,'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
  const data=await upstream.json() as any;
  if(!upstream.ok)return NextResponse.json({message:typeof data.message==='string'?data.message:'Approval not confirmed.'},{status:[400,401,404,409].includes(upstream.status)?upstream.status:503,headers});
  const a=data.approval;
  if(data.execution_allowed!==false|| (a!==null&&(!a||a.proposal_id!==id||!uuid.test(a.approval_id)||!uuid.test(a.human_identity_id)||!uuid.test(a.subject_identity_id)||!['ACTIVE','RESERVED','CONSUMED','REVOKED','EXPIRED'].includes(a.state)||!/^sha256:[a-f0-9]{64}$/.test(a.action_digest)||!Number.isFinite(Date.parse(a.expires_at))||a.execution_allowed!==false||(body&&a.action_digest!==body.action_digest))))throw new Error();
  return NextResponse.json(data,{headers});
 }catch{return NextResponse.json({message:'Approval outcome unconfirmed. Check exact approval before sending another request.'},{status:503,headers});}
}
export const GET=call;export const POST=call;

export const DELETE=call;
