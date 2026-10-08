"""Install the protected exact approval route."""
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
    location = /alexa/auth/approvals {
        proxy_pass http://127.0.0.1:8006/auth/approvals;
        proxy_http_version 1.1;
        proxy_set_header Host 127.0.0.1:8006;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 45s;
        client_max_body_size 8k;
    }
'''
    if original.count(marker) != 1:
        raise SystemExit('Expected API server block not found; stopped.')
    if 'location = /alexa/auth/approvals' in original and route.strip() not in original:
        raise SystemExit('Approval route exists with different settings; stopped.')
    if route.strip() not in original:
        backup = source.with_name(source.name + '.before-alexa-exact-approval-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
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
    subprocess.run(['systemctl', 'restart', 'ucii-alexa-lifecycle.service'], check=True)
    subprocess.run(['systemctl', 'restart', 'ucii-alexa-gateway.service'], check=True)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen('http://127.0.0.1:8006/auth/approvals', timeout=3):
                raise SystemExit('Unexpected unauthenticated proposal response; inspect gateway.')
        except urllib.error.HTTPError as error:
            if error.code == 401:
                break
            raise SystemExit(f'Unexpected proposal HTTP {error.code}; inspect gateway.')
        except (urllib.error.URLError, TimeoutError):
            time.sleep(1)
    else:
        raise SystemExit('Gateway did not become ready; inspect service status.')
    print('Exact approval HTTPS route installed. Gateway restart requires sign-in.')
    print('No approval or execution request was sent. Wait for lifecycle socket readiness before approval.')


if __name__ == '__main__':
    main()
