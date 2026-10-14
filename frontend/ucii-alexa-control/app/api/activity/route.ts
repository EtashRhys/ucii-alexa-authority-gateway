import {NextResponse} from 'next/server';
const headers={'Cache-Control':'no-store'};
export async function GET(request:Request){
 const handle=request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-ucii-session='))?.slice('__Host-ucii-session='.length)||'';
 if(!/^[A-Za-z0-9_-]{43}$/.test(handle))return NextResponse.json({message:'Sign in to view saved activity.'},{status:401,headers});
 try{
  const response=await fetch('https://api.ucii.sportgen-ai.com/alexa/auth/authority',{method:'POST',redirect:'manual',signal:AbortSignal.timeout(42000),headers:{'Content-Type':'application/json',Authorization:'Bearer '+handle},body:JSON.stringify({command:'activity'})});
  const data=await response.json() as any;
  if(response.status===401)return NextResponse.json({message:'Sign in again to view saved activity.'},{status:401,headers});
  if(!response.ok||!Array.isArray(data.activity)||data.activity.length>50||!data.activity.every((r:any)=>typeof r.id==='string'&&['tool','permission'].includes(r.kind)&&['sandbox.artifact.verify','shopping.list.edit'].includes(r.operation)&&['matched','mismatch','allowed','blocked','added','removed','already_present','not_present','created','already_exists'].includes(r.result)&&Number.isFinite(Date.parse(r.time))))throw new Error();
  return NextResponse.json({activity:data.activity},{headers});
 }catch{return NextResponse.json({message:'Saved activity unavailable. Apply the gateway update and refresh.'},{status:503,headers});}
}
