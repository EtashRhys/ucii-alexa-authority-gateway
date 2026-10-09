"""Owner-only saved list. UCII permission gates agent edits, never purchases."""
from datetime import datetime, timezone
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3
import stat
from uuid import UUID

OPERATION = 'shopping.list.edit'

@contextmanager
def connect(directory):
    directory = Path(directory)
    details = directory.lstat()
    if not stat.S_ISDIR(details.st_mode) or details.st_uid != os.getuid() or details.st_mode & 0o077:
        raise ValueError('Private shopping storage required')
    path = directory / 'shopping.sqlite3'
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    details = os.fstat(fd)
    os.close(fd)
    if not stat.S_ISREG(details.st_mode) or details.st_uid != os.getuid() or details.st_mode & 0o077:
        raise ValueError('Private shopping database required')
    db = sqlite3.connect(path, timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS items (name TEXT PRIMARY KEY)')
    db.execute('CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, command TEXT, item TEXT, result TEXT, time TEXT)')
    db.commit()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def run(request, *, agent, verify, directory):
    if (not isinstance(request, dict) or set(request) != {'version','command','item','request_id','human_token'}
            or request['version'] != 'ucii-alexa-shopping-v1' or request['command'] not in {'get','add','remove'}
            or not isinstance(request['item'], str) or str(UUID(request['request_id'])) != request['request_id']):
        raise ValueError('Invalid shopping request')
    command = request['command']
    item = ' '.join(request['item'].split()).casefold()
    if (command == 'get' and item) or (command != 'get' and (not item or len(item)>80 or any(ord(c)<32 for c in request['item']))):
        raise ValueError('Supply one short shopping item')
    action = {'operation':OPERATION, 'resource':'owner-shopping-list', 'subject_identity_id':agent,
              'command':command, 'item':item}
    # HUMAN was independently resolved by the executor before storage access.
    allowed = command == 'get' or verify(action) is True
    with connect(directory) as db:
        db.execute('BEGIN IMMEDIATE')
        previous = db.execute('SELECT command,item,result,time FROM events WHERE id=?',(request['request_id'],)).fetchone()
        if previous:
            if previous[:2] != (command,item):
                raise ValueError('Request reference reused for a different edit')
            result, checked_at = previous[2:]
        elif command == 'get':
            result, checked_at = 'viewed', datetime.now(timezone.utc).isoformat()
        else:
            allowed = allowed and verify(action) is True
            result = 'blocked'
            if allowed:
                exists = db.execute('SELECT 1 FROM items WHERE name=?',(item,)).fetchone()
                if command == 'add':
                    if not exists and db.execute('SELECT COUNT(*) FROM items').fetchone()[0] >= 100:
                        raise ValueError('Shopping list is full')
                    db.execute('INSERT OR IGNORE INTO items VALUES (?)',(item,))
                    result = 'already_present' if exists else 'added'
                else:
                    db.execute('DELETE FROM items WHERE name=?',(item,))
                    result = 'removed' if exists else 'not_present'
            checked_at = datetime.now(timezone.utc).isoformat()
            # Edit and audit record commit together; same request cannot edit twice.
            db.execute('INSERT INTO events VALUES (?,?,?,?,?)',(request['request_id'],command,item,result,checked_at))
        items = [r[0] for r in db.execute('SELECT name FROM items ORDER BY name')]
    return {'operation':OPERATION, 'request_id':request['request_id'], 'result':result,
            'items':items, 'checked_at':checked_at, 'purchased':False}

def activity(directory):
    if not (Path(directory)/'shopping.sqlite3').exists():
        return []
    with connect(directory) as db:
        return [{'id':r[0], 'kind':'tool', 'operation':OPERATION,'result':r[1],'time':r[2]}
                for r in db.execute('SELECT id,result,time FROM events ORDER BY time DESC LIMIT 50')]
