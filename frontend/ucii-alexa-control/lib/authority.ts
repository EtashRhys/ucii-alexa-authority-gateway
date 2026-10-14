export type Verification = {principal:'agent';identity_id:string;credential_fingerprint:string;algorithm:'ML-DSA-65';verification:'VERIFIED';checked_at:string;expires_at:string};
export type Identity = {principal:'human'|'agent';identity_id:string;identity_type:'HUMAN'|'AI_AGENT';name:string;record_status:'ACTIVE';verification:'UNVERIFIED';credential_fingerprint:null;checked_at:string};
export type Action = { operation:string; resource:string; environment:string; description:string; artifact_digest?:string };
export type AuthorityCheck = {operation:string;resource:string;environment:string;authority_state:string;operation_authorized:boolean;authority_id:string|null;checked_at:string;expires_at:string;execution_allowed:false};
export type Lifecycle = 'IDLE'|'ACTION_PROPOSED'|'CHECKING_AUTHORITY'|'AUTHORIZED'|'AUTHORIZATION_REQUIRED'|'DENIED'|'FAILED'|'EXECUTING'|'EXECUTED'|'REVOKING'|'REVOKED'|'CONSUMED'|'EXPIRED';
export type Connection = {ucii:'online'|'unavailable';gateway:string;conversation:string;executor:string;checked_at:string;upstream_status?:number;protocol?:string;tool?:string};
export async function gateway(path:string, payload?:unknown) {
  const response=await fetch('/api/gateway',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path,payload})});
  const data=await response.json() as { tool_result?:{status:'completed'|'blocked';request_id:string;artifact_matches:boolean|null;checked_at:string}; authority_check?:AuthorityCheck; verification?:Verification; identity?:Identity; message?:string; decision?: string; connection?:Connection };
  if(!response.ok) throw new Error(data.message || 'Authority service unavailable');
  return data;
}
