"""Explicit sandbox service install; grants no authority and executes no action."""
import grp
import hashlib
import json
import os
from pathlib import Path
import pwd
import shlex
import subprocess
import time
from uuid import UUID

if os.geteuid()!=0:raise SystemExit('Run with sudo python3 deploy/install_executor.py')
root=Path('/opt/ucii/ucii-alexa-authority-gateway')
unit=Path('/etc/systemd/system/ucii-alexa-executor.service')
artifact_root=Path('/etc/ucii-alexa-executor')
artifact=artifact_root/'artifact.json'
if unit.exists() or unit.is_symlink() or artifact_root.exists() or artifact_root.is_symlink():
    raise SystemExit('Executor installation already started; inspect state rather than overwriting.')
for group in ('ucii-database','ucii-alexa-signer-ipc'):grp.getgrnam(group)
settings=subprocess.check_output(['systemctl','show','ucii-alexa-gateway.service','--property=Environment','--value'],text=True)
allowed={'UCII_ALEXA_HUMAN_ID','UCII_ALEXA_AGENT_ID','UCII_ALEXA_AGENT_CREDENTIAL_ID','UCII_ALEXA_AGENT_FINGERPRINT'}
bindings={}
for entry in shlex.split(settings):
    name,_,value=entry.partition('=')
    if name in allowed:bindings[name]=value
if set(bindings)!=allowed:raise SystemExit('Required gateway identity bindings unavailable')
for name,value in bindings.items():
    if name.endswith('FINGERPRINT'):
        if len(value)!=64 or any(c not in '0123456789abcdef' for c in value):raise SystemExit('Invalid credential fingerprint')
    elif str(UUID(value))!=value:raise SystemExit('Invalid identity binding')
user='ucii-alexa-executor';group='ucii-alexa-executor-ipc'
try:grp.getgrnam(group)
except KeyError:subprocess.run(['groupadd','--system',group],check=True)
try:
    details=pwd.getpwnam(user)
    if details.pw_gid!=grp.getgrnam(group).gr_gid or details.pw_shell!='/usr/sbin/nologin':
        raise SystemExit('Unexpected existing executor user; stopped')
except KeyError:
    subprocess.run(['useradd','--system','--gid',group,'--no-create-home','--home-dir','/nonexistent','--shell','/usr/sbin/nologin',user],check=True)
artifact_root.mkdir(mode=0o755)
content=b'{"product":"ucii-alexa","resource":"test-app","environment":"staging","purpose":"sandbox-artifact-verification","version":1}\n'
fd=os.open(artifact,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
with os.fdopen(fd,'wb') as stream:stream.write(content);stream.flush();os.fsync(stream.fileno())
subprocess.run(['install','-m','644',str(root/'deploy/ucii-alexa-executor.service'),str(unit)],check=True)
dropin=Path(str(unit)+'.d');dropin.mkdir(mode=0o755)
with (dropin/'identities.conf').open('x') as stream:
    stream.write('[Service]\n'+''.join('Environment='+name+'='+value+'\n' for name,value in sorted(bindings.items())))
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','enable','--now','ucii-alexa-executor.service'],check=True)
# Socket existence is read-only; never connect and send an execution probe here.
for attempt in range(60):
    if Path('/run/ucii-alexa-executor/executor.sock').is_socket():
        print('PASS: protected sandbox executor socket exists.')
        print('Sandbox artifact digest: sha256:'+hashlib.sha256(content).hexdigest())
        print('No authority granted, approval issued, or execution requested.')
        break
    time.sleep(1)
else:raise SystemExit('Socket not ready; inspect ucii-alexa-executor.service logs. Do not reinstall.')
