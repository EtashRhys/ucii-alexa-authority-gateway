"""Session deadlines and rotation tested against a mock UCII HTTP boundary."""
import asyncio
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gateway"))
import auth
import httpx


def token(exp, label='old'):
    payload = base64.urlsafe_b64encode(json.dumps({'exp': exp}).encode()).decode().rstrip('=')
    return 'header.' + payload + '.' + label


class Routes:
    def __init__(self):
        self.routes = {}
    def custom_route(self, path, methods):
        def register(fn):
            self.routes[path] = fn
            return fn
        return register


def request(body=None, handle=None, method='POST'):
    async def read():
        return json.dumps(body).encode()
    return SimpleNamespace(body=read, method=method, headers={
        'content-type': 'application/json',
        'authorization': 'Bearer ' + handle if handle else '',
    })


class SessionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.old = token(time.time() + 3600)
        self.new = token(time.time() + 7200, 'new')
        self.refreshes = 0
        self.login_bodies = []
        self.valid_tokens = {self.old}
        self.release_refresh = None
        self.fail_refresh = False
        self.refreshed = asyncio.Event()
        self.env = patch.dict(os.environ, {
            'UCII_ALEXA_HUMAN_ID': 'human', 'UCII_ALEXA_AGENT_ID': 'agent',
            'UCII_ALEXA_AGENT_FINGERPRINT': 'f' * 64,
        })
        self.env.start()
        real_client = httpx.AsyncClient
        async def upstream(req):
            if req.url.path == '/v1/auth/login':
                self.login_bodies.append(json.loads(req.content))
                return httpx.Response(200, json={'access_token': self.old})
            if req.url.path == '/v1/auth/refresh':
                self.refreshes += 1
                if self.fail_refresh:
                    self.refreshed.set()
                    return httpx.Response(503)
                self.valid_tokens.discard(json.loads(req.content)['token'])
                self.valid_tokens.add(self.new)
                self.refreshed.set()
                if self.release_refresh is not None:
                    await self.release_refresh.wait()
                return httpx.Response(200, json={'access_token': self.new})
            bearer = req.headers.get('authorization', '').removeprefix('Bearer ')
            return httpx.Response(200, json={'identity_id': 'human'}) if bearer in self.valid_tokens else httpx.Response(401)
        self.mock = patch.object(auth.httpx, 'AsyncClient', side_effect=lambda **kwargs: real_client(transport=httpx.MockTransport(upstream), **kwargs))
        self.mock.start()
        self.routes = Routes()
        auth.install_auth_routes(self.routes, lambda msg: b'test-signature')
        fn = self.routes.routes['/auth/session']
        self.sessions = dict(zip(fn.__code__.co_freevars, [cell.cell_contents for cell in fn.__closure__]))['sessions']

    async def asyncTearDown(self):
        tasks = [entry['renewal'] for entry in self.sessions.values()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.mock.stop()
        self.env.stop()

    async def login(self, minutes=60):
        response = await self.routes.routes['/auth/login'](request({'email': 'owner@example.test', 'password': 'password123', 'duration_minutes': minutes}))
        return response, json.loads(response.body)

    async def test_selected_deadlines_and_no_duration_forwarded_to_ucii(self):
        for minutes in (15, 60, 240):
            response, data = await self.login(minutes)
            self.assertEqual(response.status_code, 200)
            remaining = datetime.fromisoformat(data['expires_at']).timestamp() - time.time()
            self.assertAlmostEqual(remaining, minutes * 60, delta=2)
            self.assertNotIn('duration_minutes', self.login_bodies[-1])
            self.assertNotIn('access_token', data)

    async def test_arbitrary_and_boolean_durations_rejected(self):
        for minutes in (8, 10000, True, '240'):
            response, _ = await self.login(minutes)
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.login_bodies, [])

    async def test_expired_deadline_rejected_and_renewal_cancelled(self):
        _, data = await self.login(240)
        entry = self.sessions[data['session']]
        entry['deadline'] = time.monotonic() - 1
        response = await self.routes.routes['/auth/session'](request(handle=data['session'], method='GET'))
        self.assertEqual(response.status_code, 401)
        self.assertNotIn(data['session'], self.sessions)

    async def test_logout_removes_handle(self):
        _, data = await self.login(240)
        response = await self.routes.routes['/auth/session'](request(handle=data['session'], method='DELETE'))
        self.assertEqual(response.status_code, 200)
        response = await self.routes.routes['/auth/session'](request(handle=data['session'], method='GET'))
        self.assertEqual(response.status_code, 401)

    async def test_background_rotation_preserves_absolute_deadline(self):
        self.old = token(time.time() + 299)
        self.valid_tokens = {self.old}
        _, data = await self.login(240)
        await asyncio.wait_for(self.refreshed.wait(), 1)
        response = await self.routes.routes['/auth/session'](request(handle=data['session'], method='GET'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body)['expires_at'], data['expires_at'])
        self.assertEqual(self.sessions[data['session']]['token'], self.new)
        self.assertEqual(self.refreshes, 1)

    async def test_session_waits_for_in_flight_rotation(self):
        self.old = token(time.time() + 299)
        self.valid_tokens = {self.old}
        self.release_refresh = asyncio.Event()
        _, data = await self.login(240)
        await asyncio.wait_for(self.refreshed.wait(), 1)
        pending = asyncio.create_task(self.routes.routes['/auth/session'](request(handle=data['session'], method='GET')))
        await asyncio.sleep(0)
        self.assertFalse(pending.done())
        self.release_refresh.set()
        response = await asyncio.wait_for(pending, 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.refreshes, 1)

    async def test_failed_rotation_discards_session(self):
        self.old = token(time.time() + 299)
        self.valid_tokens = {self.old}
        self.fail_refresh = True
        _, data = await self.login(240)
        await asyncio.wait_for(self.refreshed.wait(), 1)
        response = await self.routes.routes['/auth/session'](request(handle=data['session'], method='GET'))
        self.assertEqual(response.status_code, 401)

    async def test_authority_without_session_rejected(self):
        response = await self.routes.routes['/auth/authority'](request({'command': 'grant', 'operation': 'infrastructure.deploy', 'confirmation': 'GRANT_OPERATION_AUTHORITY'}))
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
