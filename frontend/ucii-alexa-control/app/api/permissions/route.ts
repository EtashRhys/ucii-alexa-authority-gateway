import {NextResponse} from 'next/server';
import {GET as sessionStatus} from '../auth/route';
const headers={'Cache-Control':'no-store'};
async function change(request:Request,mode:string,operation:string){
 if(request.method!=='GET'&&request.headers.get('origin')!==new URL(request.url).origin)return NextResponse.json({message:'Request origin rejected.'},{status:403,headers});
 const response=await sessionStatus(request);const session=await response.json() as any;
 if(!response.ok||session.authentication!=='AUTHENTICATED')return NextResponse.json({message:'Sign in to view or change your saved permissions.'},{status:401,headers});
 const handle=request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-ucii-session='))?.slice('__Host-ucii-session='.length)||'';
 if(!/^[A-Za-z0-9_-]{43}$/.test(handle))return NextResponse.json({message:'Sign in again.'},{status:401,headers});
 try{
  const upstream=await fetch('https://api.ucii.sportgen-ai.com/alexa/auth/authority',{method:'POST',redirect:'manual',signal:AbortSignal.timeout(42000),headers:{'Content-Type':'application/json',Authorization:'Bearer '+handle},body:JSON.stringify({command:'tool_permission',operation,mode,confirmation:mode==='get'?'':'CONFIRM_TOOL_PERMISSION'})});
  const data=await upstream.json() as any;const p=data.permission;
  if(!upstream.ok||p?.operation!==operation||!['ALLOWED','BLOCKED'].includes(p.mode)||typeof p.subject_identity_id!=='string')throw new Error();
  return NextResponse.json({permission:p},{headers});
 }catch{return NextResponse.json({message:'Saved permission could not be confirmed. Refresh after the gateway update; do not assume a change succeeded.'},{status:503,headers});}
}
export async function GET(request:Request){const operation=new URL(request.url).searchParams.get('operation')||'sandbox.artifact.verify';if(!['sandbox.artifact.verify','shopping.list.edit'].includes(operation))return NextResponse.json({message:'Unknown permission.'},{status:400,headers});return change(request,'get',operation);}
export async function POST(request:Request){try{const body=await request.json() as any;if(!['confirmation,mode','confirmation,mode,operation'].includes(Object.keys(body).sort().join(','))||!['sandbox.artifact.verify','shopping.list.edit'].includes(body.operation||'sandbox.artifact.verify')||!['allow','block'].includes(body.mode)||body.confirmation!=='CONFIRM_TOOL_PERMISSION')throw new Error();return change(request,body.mode,body.operation||'sandbox.artifact.verify');}catch{return NextResponse.json({message:'Confirm Allow or Block.'},{status:400,headers});}}
