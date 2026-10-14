import {NextResponse} from 'next/server';
const endpoint='https://api.ucii.sportgen-ai.com/alexa/auth';
const headers={'Cache-Control':'no-store'};
const cookieName='__Host-ucii-session';
const options={httpOnly:true,secure:true,sameSite:'strict' as const,path:'/'};
function handle(request:Request){return request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith(cookieName+'='))?.slice(cookieName.length+1)||'';}
function clear(response:NextResponse){response.cookies.set(cookieName,'',{...options,maxAge:0});return response;}
function allowed(request:Request){return request.headers.get('origin')===new URL(request.url).origin;}
function valid(data:any,minutes=240){const remaining=Date.parse(data.expires_at)-Date.now();return data.authentication==='AUTHENTICATED'&&typeof data.identity_id==='string'&&Number.isFinite(remaining)&&remaining>0&&remaining<=minutes*60000+5000;}
export async function GET(request:Request){
 const session=handle(request);
 if(!/^[A-Za-z0-9_-]{43}$/.test(session))return clear(NextResponse.json({authentication:'SIGNED_OUT'},{headers}));
 try{
  const response=await fetch(endpoint+'/session',{redirect:'manual',signal:AbortSignal.timeout(35000),headers:{Authorization:'Bearer '+session}});
  if(response.status===401)return clear(NextResponse.json({authentication:'SIGNED_OUT'},{headers}));
  if(!response.ok)throw new Error();
  const data=await response.json() as {authentication?:string;identity_id:string;expires_at:string;session:string;message?:string};if(!valid(data))throw new Error();
  return NextResponse.json({authentication:data.authentication,identity_id:data.identity_id,expires_at:data.expires_at},{headers});
 }catch{return NextResponse.json({message:'Session check unavailable. Protected controls remain blocked.'},{status:503,headers});}
}
export async function POST(request:Request){
 if(!allowed(request))return NextResponse.json({message:'Request origin rejected.'},{status:403,headers});
 let body:any;try{const raw=await request.text();if(raw.length>4096)throw new Error();body=JSON.parse(raw);if(![15,60,240].includes(body.duration_minutes)||typeof body.email!=='string'||typeof body.password!=='string'||body.password.length<8||body.password.length>1024||body.email.length>254)throw new Error();}catch{return NextResponse.json({message:'Enter your email and password (8+ characters).'},{status:400,headers});}
 try{
  const response=await fetch(endpoint+'/login',{method:'POST',redirect:'manual',signal:AbortSignal.timeout(145000),headers:{'Content-Type':'application/json'},body:JSON.stringify({email:body.email,password:body.password,duration_minutes:body.duration_minutes})});
  if(!response.ok)return NextResponse.json({message:response.status===401?'Login could not be verified.':response.status===429?'Too many attempts. Try again in a minute.':'UCII login unavailable. Please retry.'},{status:[401,429].includes(response.status)?response.status:503,headers});
  const data=await response.json() as {authentication?:string;identity_id:string;expires_at:string;session:string;message?:string};if(!valid(data,body.duration_minutes)||! /^[A-Za-z0-9_-]{43}$/.test(data.session))throw new Error();
  const result=NextResponse.json({authentication:data.authentication,identity_id:data.identity_id,expires_at:data.expires_at},{headers});
  result.cookies.set(cookieName,data.session,{...options,maxAge:Math.max(1,Math.floor((Date.parse(data.expires_at)-Date.now())/1000))});
  return result;
 }catch{return NextResponse.json({message:'UCII login could not complete. Please retry.'},{status:503,headers});}
}
export async function DELETE(request:Request){
 if(!allowed(request))return NextResponse.json({message:'Request origin rejected.'},{status:403,headers});
 const session=handle(request);
 try{if(/^[A-Za-z0-9_-]{43}$/.test(session))await fetch(endpoint+'/session',{method:'DELETE',redirect:'manual',signal:AbortSignal.timeout(35000),headers:{Authorization:'Bearer '+session}});}catch{}
 return clear(NextResponse.json({authentication:'SIGNED_OUT'},{headers}));
}
