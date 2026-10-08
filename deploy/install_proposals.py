"""Install the bounded draft route and private gateway state directory."""
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
import urllib.error


def main():
    if os.geteuid() != 0:
        raise SystemExit('Run this installer with sudo.')
    subprocess.run(['systemctl', 'cat', 'ucii-alexa-gateway.service'], check=True, stdout=subprocess.DEVNULL)
    source = Path('/etc/nginx/sites-enabled/ucii').resolve()
    original = source.read_text()
    marker = '    server_name api.ucii.sportgen-ai.com;'
    route = '''
    location = /alexa/auth/proposals {
        proxy_pass http://127.0.0.1:8006/auth/proposals;
        proxy_http_version 1.1;
        proxy_set_header Host 127.0.0.1:8006;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 45s;
        client_max_body_size 8k;
    }
'''
    if original.count(marker) != 1:
        raise SystemExit('Expected API server block not found; stopped.')
    if 'location = /alexa/auth/proposals' in original and route.strip() not in original:
        raise SystemExit('Proposal route exists with different settings; stopped.')
    dropin = Path('/etc/systemd/system/ucii-alexa-gateway.service.d/proposals.conf')
    contents = '[Service]\nStateDirectory=ucii-alexa-gateway\nStateDirectoryMode=0700\nEnvironment=UCII_ALEXA_PROPOSALS_PATH=/var/lib/ucii-alexa-gateway/proposals.sqlite3\n'
    if dropin.is_symlink() or (dropin.exists() and dropin.read_text() != contents):
        raise SystemExit('Unexpected proposal service settings; stopped.')
    if route.strip() not in original:
        backup = source.with_name(source.name + '.before-alexa-proposals-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        if backup.exists():
            raise SystemExit('Backup already exists; stopped.')
        shutil.copy2(source, backup)
        source.write_text(original.replace(marker, marker + '\n' + route, 1))
        result = subprocess.run(['nginx', '-t'])
        if result.returncode:
            shutil.copy2(backup, source)
            raise SystemExit('Nginx validation failed; original restored.')
        subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
        print('Nginx backup:', backup)
    else:
        subprocess.run(['nginx', '-t'], check=True)
    dropin.parent.mkdir(parents=True, exist_ok=True)
    dropin.write_text(contents)
    dropin.chmod(0o644)
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', 'restart', 'ucii-alexa-gateway.service'], check=True)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen('http://127.0.0.1:8006/auth/proposals', timeout=3):
                raise SystemExit('Unexpected unauthenticated proposal response; inspect gateway.')
        except urllib.error.HTTPError as error:
            if error.code == 401:
                break
            raise SystemExit(f'Unexpected proposal HTTP {error.code}; inspect gateway.')
        except (urllib.error.URLError, TimeoutError):
            time.sleep(1)
    else:
        raise SystemExit('Gateway did not become ready; inspect service status.')
    print('Proposal storage and HTTPS route installed. Gateway restart requires sign-in.')
    print('No approval, authority grant or execution request was sent.')


if __name__ == '__main__':
    main()
