import {NextResponse} from 'next/server';
const headers={'Cache-Control':'no-store'};
export async function POST(request:Request){
 if(request.headers.get('origin')!==new URL(request.url).origin)return NextResponse.json({message:'Request origin rejected.'},{status:403,headers});
 const handle=request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-ucii-session='))?.slice('__Host-ucii-session='.length)||'';
 if(!/^[A-Za-z0-9_-]{43}$/.test(handle))return NextResponse.json({message:'Sign in to view or change your personal shopping list.'},{status:401,headers});
 try{
  const body=await request.json() as any;
  if(!['action,item,request_id','action,item,list_name,request_id'].includes(Object.keys(body).sort().join(','))||!['get','create','add','remove'].includes(body.action)||(body.list_name!==undefined&&(typeof body.list_name!=='string'||!body.list_name.trim()||body.list_name.length>60))||typeof body.item!=='string'||body.item.length>160||!/^[-0-9a-f]{36}$/.test(body.request_id))return NextResponse.json({message:'Supply one shopping item.'},{status:400,headers});
  const response=await fetch('https://api.ucii.sportgen-ai.com/alexa/auth/authority',{method:'POST',redirect:'manual',signal:AbortSignal.timeout(42000),headers:{'Content-Type':'application/json',Authorization:'Bearer '+handle},body:JSON.stringify({command:'shopping',...body})});
  const data=await response.json() as any;
  if(response.status===401)return NextResponse.json({message:'Sign in again to use your shopping list.'},{status:401,headers});
  const s=data.shopping;
  if(!response.ok||s?.operation!=='shopping.list.edit'||s.request_id!==body.request_id||s.purchased!==false||!['viewed','created','already_exists','added','removed','blocked','already_present','not_present'].includes(s.result)||!Array.isArray(s.items)||s.items.length>100||!s.items.every((i:unknown)=>typeof i==='string'&&i.length<=80))throw new Error();
  if(s.lists!==undefined&&(!Array.isArray(s.lists)||s.lists.length>12||!s.lists.every((name:unknown)=>typeof name==='string'&&name.length<=60)))throw new Error();
  return NextResponse.json({shopping:{...s,list_name:s.list_name||'Shopping list',lists:s.lists||['Shopping list']}},{headers});
 }catch{return NextResponse.json({message:'Shopping result not confirmed. Retrieve your list before repeating an edit. The server update may still be needed.'},{status:503,headers});}
}
