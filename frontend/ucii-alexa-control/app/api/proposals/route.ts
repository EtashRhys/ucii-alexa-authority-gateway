import {NextResponse} from 'next/server';
const endpoint='https://api.ucii.sportgen-ai.com/alexa/auth/proposals';
const headers={'Cache-Control':'no-store'};
const uuid=/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/;
function sessionHandle(request:Request){return request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-ucii-session='))?.slice('__Host-ucii-session='.length)||'';}
async function call(request:Request){
 if(request.method!=='GET'&&request.headers.get('origin')!==new URL(request.url).origin)return NextResponse.json({message:'Request origin rejected.'},{status:403,headers});
 const handle=sessionHandle(request);
 if(!/^[A-Za-z0-9_-]{43}$/.test(handle))return NextResponse.json({message:'Sign in with UCII to save an exact proposal.'},{status:401,headers});
 let body:any, suffix='';
 try{
  if(request.method==='GET'){
   const id=new URL(request.url).searchParams.get('proposal_id')||'';
   if(!uuid.test(id))throw new Error();
   suffix='?proposal_id='+id;
  }else{
   const raw=await request.text();if(raw.length>8192)throw new Error();body=JSON.parse(raw);
   if(request.method==='DELETE'){if(Object.keys(body).sort().join(',')!=='proposal_id'||!uuid.test(body.proposal_id))throw new Error();}
   else{
    if(Object.keys(body).sort().join(',')!=='action,idempotency_key'||!uuid.test(body.idempotency_key)||!body.action)throw new Error();
    const a=body.action;
    if(!['environment,operation,resource','artifact_digest,environment,operation,resource'].includes(Object.keys(a).sort().join(','))||typeof a.operation!=='string'||! /^[A-Za-z][A-Za-z0-9_.:-]{0,127}$/.test(a.operation)||typeof a.resource!=='string'||!a.resource.trim()||a.resource!==a.resource.trim()||a.resource.length>512||/[\x00-\x1f\x7f*?]/.test(a.resource)||!['staging','production','not applicable'].includes(a.environment))throw new Error();
    if(a.artifact_digest!==undefined&&!/^sha256:[a-f0-9]{64}$/.test(a.artifact_digest))throw new Error();
    if(a.operation==='infrastructure.deploy'&&(!a.artifact_digest||a.environment==='not applicable'))throw new Error();
   }
  }
 }catch{return NextResponse.json({message:'Supply an exact action and a sha256 artifact digest for deployment.'},{status:400,headers});}
 try{
  const upstream=await fetch(endpoint+suffix,{method:request.method,redirect:'manual',signal:AbortSignal.timeout(40000),headers:{Authorization:'Bearer '+handle,'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
  const data=await upstream.json() as any;
  if(!upstream.ok)return NextResponse.json({message:typeof data.message==='string'?data.message:'Proposal request failed.'},{status:[400,401,404,409,413,429].includes(upstream.status)?upstream.status:503,headers});
  const p=data.proposal,a=p?.action;
  if(!p||!uuid.test(p.proposal_id)||!a||a.version!=='ucii-alexa-action-v1'||!uuid.test(a.subject_identity_id)||!['NOT_ESTABLISHED','CHECK_REQUIRED'].includes(p.approval)||p.execution_allowed!==false||!['PROPOSED','CANCELLED','EXPIRED','APPROVAL_PENDING','APPROVED','APPROVAL_REVOKED'].includes(p.state)||!/^sha256:[a-f0-9]{64}$/.test(p.action_digest)||!Number.isFinite(Date.parse(p.expires_at))||Date.parse(p.expires_at)-Date.parse(p.created_at)!==900000)throw new Error();
  if(request.method==='GET'&&p.proposal_id!==new URL(request.url).searchParams.get('proposal_id'))throw new Error();
  if(request.method==='DELETE'&&p.proposal_id!==body.proposal_id)throw new Error();
  if(request.method==='POST'&&(a.operation!==body.action.operation||a.resource!==body.action.resource||a.environment!==body.action.environment||a.artifact_digest!==(body.action.artifact_digest??null)))throw new Error();
  const canonical=JSON.stringify(Object.fromEntries(Object.keys(a).sort().map(key=>[key,a[key]])));
  const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical));
  const hex=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
  if(p.action_digest!=='sha256:'+hex)throw new Error();
  return NextResponse.json({proposal:p},{headers});
 }catch{return NextResponse.json({message:'Proposal outcome could not be confirmed. Retry the unchanged draft to retrieve the same request; check exact approval separately; execution remains blocked.'},{status:503,headers});}
}
export const GET=call;export const POST=call;export const DELETE=call;
