const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const source = fs.readFileSync('app/api/gateway/route.ts','utf8');
const code = ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText;
let currentSession, calls;
const NextResponse = {json:(body,options={})=>new Response(JSON.stringify(body),{status:options.status||200,headers:options.headers})};
const moduleValue = {exports:{}};
new Function('require','module','exports',code)(name=>name==='next/server'?{NextResponse}:{GET:async()=>NextResponse.json(currentSession)},moduleValue,moduleValue.exports);
global.fetch = async(_url,options)=>{
 calls++;
 const body=JSON.parse(options.body);
 const identity={principal:'human',identity_id:'owner-A',name:'Private owner',identity_type:'HUMAN',verification:'UNVERIFIED',record_status:'ACTIVE'};
 const result=body.method==='initialize'?{protocolVersion:'2025-11-25'}:body.method==='tools/list'?{tools:[{name:'ucii_identity'}]}:body.method==='tools/call'?{structuredContent:identity}:{};
 return new Response(JSON.stringify({jsonrpc:'2.0',id:body.id,result}));
};
async function run(session){currentSession=session;calls=0;return moduleValue.exports.POST(new Request('https://demo.test/api/gateway',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:'identity.get',payload:{principal:'human'}})}));}
(async()=>{
 let r=await run({authentication:'SIGNED_OUT'});assert.equal(r.status,401);assert.equal(calls,0);
 r=await run({authentication:'AUTHENTICATED',identity_id:'owner-B'});assert.equal(r.status,403);assert.equal((await r.text()).includes('Private owner'),false);
 r=await run({authentication:'AUTHENTICATED',identity_id:'owner-A'});assert.equal(r.status,200);assert.equal((await r.json()).identity.identity_id,'owner-A');
 console.log('PASS: anonymous identity requests stop before MCP; other users cannot receive owner identity; matching owner can retrieve it.');
})();
