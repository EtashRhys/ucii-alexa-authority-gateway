import { NextResponse } from 'next/server';
import {GET as sessionStatus} from '../auth/route';
const headers = {'Cache-Control':'no-store'};
const endpoint = 'https://api.ucii.sportgen-ai.com/alexa/mcp';
async function rpc(id:number, method:string, params:unknown, protocol?:string) {
  const response = await fetch(endpoint, {
    method:'POST', redirect:'manual', signal:AbortSignal.timeout(15000),
    headers:{'Content-Type':'application/json',Accept:'application/json, text/event-stream',...(protocol?{'MCP-Protocol-Version':protocol}:{})},
    body:JSON.stringify({jsonrpc:'2.0',id,method,params}),
  });
  if(!response.ok)throw new Error(`MCP ${method} returned HTTP ${response.status}`);
  const data = await response.json() as {jsonrpc?:string;id?:number;error?:unknown;result?:any};
  if(data.jsonrpc!=='2.0'||data.id!==id||data.error||!data.result)throw new Error(`Invalid MCP ${method} response`);
  return data.result;
}
export async function POST(request:Request) {
  let body:{path?:string;payload?:{principal?:string;operation?:string;resource?:string;environment?:string}};
  try{body=await request.json();}catch{return NextResponse.json({message:'Invalid request.'},{status:400,headers});}
  if(!['health','identity.get','agent.verify','authorization.check','artifact.verify'].includes(body.path||''))return NextResponse.json({code:'INTEGRATION_NOT_CONFIGURED',message:'This control still needs identity and protected authority wiring.'},{status:503,headers});
  if(body.path==='artifact.verify'&&request.headers.get('origin')!==new URL(request.url).origin)return NextResponse.json({message:'Request origin rejected.'},{status:403,headers});
  if(body.path==='authorization.check'){
    if(request.headers.get('origin')!==new URL(request.url).origin)return NextResponse.json({message:'Request origin rejected.'},{status:403,headers});
    if(typeof body.payload?.operation!=='string'||! /^[A-Za-z][A-Za-z0-9_.:-]{0,127}$/.test(body.payload.operation)||typeof body.payload.resource!=='string'||!body.payload.resource.trim()||body.payload.resource.length>512||!['staging','production','not applicable'].includes(body.payload.environment||''))return NextResponse.json({message:'Supply an exact operation and resource.'},{status:400,headers});
    const response=await sessionStatus(request);
    const session=await response.json() as {authentication?:string};
    if(!response.ok)return NextResponse.json({message:'HUMAN session could not be checked. Please retry.'},{status:503,headers});
    if(session.authentication!=='AUTHENTICATED')return NextResponse.json({message:'Sign in with UCII before checking authority.'},{status:401,headers});
  }
  if(body.path==='identity.get'&&!['human','agent'].includes(body.payload?.principal||''))return NextResponse.json({message:'Choose human or agent.'},{status:400,headers});
  let humanOwner:string|undefined;
  if(body.path==='identity.get'&&body.payload?.principal==='human'){
    const response=await sessionStatus(request);
    const session=await response.json() as {authentication?:string;identity_id?:string};
    if(!response.ok)return NextResponse.json({message:'Your session could not be checked.'},{status:503,headers});
    if(session.authentication!=='AUTHENTICATED'||!session.identity_id)return NextResponse.json({message:'Sign in to retrieve your own identity.'},{status:401,headers});
    humanOwner=session.identity_id;
  }
  const tool=body.path==='artifact.verify'?'ucii_artifact_verify':body.path==='authorization.check'?'ucii_authority_check':body.path==='agent.verify'?'ucii_agent_verify':body.path==='identity.get'?'ucii_identity':'ucii_health';
  const checked_at=new Date().toISOString();
  let gateway='unavailable';
  try{
    const initialized=await rpc(1,'initialize',{protocolVersion:'2025-11-25',capabilities:{},clientInfo:{name:'ucii-alexa-website',version:'0.2.0'}});
    if(initialized.protocolVersion!=='2025-11-25')throw new Error('Unsupported MCP protocol');
    const protocol=initialized.protocolVersion;
    const notification=await fetch(endpoint,{method:'POST',redirect:'manual',signal:AbortSignal.timeout(15000),headers:{'Content-Type':'application/json',Accept:'application/json, text/event-stream','MCP-Protocol-Version':protocol},body:JSON.stringify({jsonrpc:'2.0',method:'notifications/initialized'})});
    if(!notification.ok)throw new Error(`MCP initialization notification returned HTTP ${notification.status}`);
    const listed=await rpc(2,'tools/list',{},protocol);
    if(!Array.isArray(listed.tools)||!listed.tools.some((entry:{name?:string})=>entry.name===tool))throw new Error('Requested UCII tool missing');
    gateway='online';
    const result=await rpc(3,'tools/call',{name:tool,arguments:body.path==='authorization.check'?{operation:body.payload?.operation}:body.path==='identity.get'?{principal:body.payload?.principal}:{}},protocol);
    if(result.isError)throw new Error('UCII tool failed');
    const data=result.structuredContent??JSON.parse(result.content.find((item:{type?:string})=>item.type==='text').text);
    if(body.path==='artifact.verify'){
      if(data.operation!=='sandbox.artifact.verify'||data.resource!=='test-app'||data.environment!=='staging'||!['completed','blocked'].includes(data.status)||data.deployed!==false||typeof data.request_id!=='string'||!Number.isFinite(Date.parse(data.checked_at))||(data.status==='completed'?typeof data.artifact_matches!=='boolean':data.artifact_matches!==null))throw new Error('Invalid fixed tool result');
      return NextResponse.json({tool_result:data,message:data.status==='blocked'?'UCII blocked this tool. Its saved permission must be allowed on the Permissions page.':data.artifact_matches?'The fixed staging test artifact matches. Result recorded; nothing deployed.':'The fixed artifact did not match. Result recorded; nothing deployed.'},{headers});
    }
    if(body.path==='authorization.check'){
      const bound=await rpc(4,'tools/call',{name:'ucii_identity',arguments:{principal:'agent'}},protocol);
      if(bound.isError)throw new Error('Agent identity binding unavailable');
      const identity=bound.structuredContent??JSON.parse(bound.content.find((item:{type?:string})=>item.type==='text').text);
      const age=Date.now()-Date.parse(data.checked_at);
      const active=data.authority_state==='ACTIVE';
      if(data.identity_id!==identity.identity_id||identity.record_status!=='ACTIVE'||identity.identity_type!=='AI_AGENT'||data.operation!==body.payload?.operation||! /^[a-f0-9]{64}$/.test(data.credential_fingerprint)||!['ACTIVE','NOT_GRANTED','REVOKED','EXPIRED','INVALID'].includes(data.authority_state)||data.operation_authorized!==active||data.executed!==false||data.execution_allowed!==false||data.evaluation_scope!=='operation only'||data.resource_evaluated!==false||data.environment_evaluated!==false||!Number.isFinite(age)||age < -5000||age>30000||(active?(typeof data.authority_id!=='string'||!data.authority_id.trim()):data.authority_id!==null))throw new Error('Invalid delegated authority evidence');
      return NextResponse.json({decision:active?'AUTHORIZATION_REQUIRED':'DENIED',authority_check:{...data,resource:body.payload?.resource,environment:body.payload?.environment,expires_at:new Date(Date.parse(data.checked_at)+60000).toISOString()},message:active?'UCII found operation authority. Resource and environment approval remain unverified; execution is blocked.':`UCII returned ${data.authority_state} for ${data.operation}. Execution is blocked.`},{headers});
    }
    if(body.path==='agent.verify'){
      const bound=await rpc(4,'tools/call',{name:'ucii_identity',arguments:{principal:'agent'}},protocol);
      if(bound.isError)throw new Error('Agent identity binding unavailable');
      const identity=bound.structuredContent??JSON.parse(bound.content.find((item:{type?:string})=>item.type==='text').text);
      const age=Date.now()-Date.parse(data.checked_at);
      if(data.principal!=='agent'||data.identity_id!==identity.identity_id||identity.record_status!=='ACTIVE'||data.verification!=='VERIFIED'||data.algorithm!=='ML-DSA-65'||!/^([a-f0-9]{64})$/.test(data.credential_fingerprint)||!Number.isFinite(age)||age < -5000||age>30000)throw new Error('Invalid agent verification evidence');
      return NextResponse.json({verification:{...data,expires_at:new Date(Date.parse(data.checked_at)+60000).toISOString()},message:'Agent credential proof verified by UCII. Action authority remains separate.'},{headers});
    }
    if(body.path==='identity.get'){
      if(data.principal!==body.payload?.principal||typeof data.identity_id!=='string'||typeof data.name!=='string'||data.verification!=='UNVERIFIED'||data.record_status!=='ACTIVE'||data.identity_type!==(data.principal==='human'?'HUMAN':'AI_AGENT'))throw new Error('Invalid identity tool result');
      if(data.principal==='human'&&data.identity_id!==humanOwner)return NextResponse.json({message:'This identity does not belong to your session.'},{status:403,headers});
      return NextResponse.json({identity:data,message:'Active identity record retrieved. Credential possession remains unverified.'},{headers});
    }
    if(!['online','unavailable'].includes(data.ucii)||typeof data.checked_at!=='string')throw new Error('Invalid health tool result');
    return NextResponse.json({connection:{ucii:data.ucii,gateway,conversation:'not configured',executor:'not configured',checked_at,protocol,tool:'ucii_health'},message:data.ucii==='online'?'MCP gateway and UCII are online. Public health checks, controlled artifact checks, permissions and Activity are connected.':'MCP gateway is online, but UCII health is unavailable.'},{headers});
  }catch(error){
    const detail=error instanceof Error?error.message.slice(0,240):'Unknown connection failure';
    console.error('UCII MCP check failed:',detail);
    if(body.path!=='health')return NextResponse.json({message:`UCII request failed — ${detail}`},{status:502,headers});
    return NextResponse.json({connection:{ucii:'unavailable',gateway,conversation:'not configured',executor:'not configured',checked_at},message:`MCP connection check failed — ${detail}`},{headers});
  }
}
