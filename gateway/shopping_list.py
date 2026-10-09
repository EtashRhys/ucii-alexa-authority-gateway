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
    db.execute('BEGIN IMMEDIATE')
    migrate = not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='named_items'").fetchone()
    db.execute('CREATE TABLE IF NOT EXISTS lists (name TEXT PRIMARY KEY, label TEXT NOT NULL)')
    db.execute("INSERT OR IGNORE INTO lists VALUES ('shopping list','Shopping list')")
    db.execute('CREATE TABLE IF NOT EXISTS named_items (list_name TEXT, name TEXT, PRIMARY KEY(list_name,name))')
    db.execute('CREATE TABLE IF NOT EXISTS items (name TEXT PRIMARY KEY)')
    if migrate:
        db.execute("INSERT OR IGNORE INTO named_items SELECT 'shopping list',name FROM items")
    db.execute('CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, command TEXT, item TEXT, result TEXT, time TEXT)')
    if 'list_name' not in {r[1] for r in db.execute('PRAGMA table_info(events)')}:
        db.execute("ALTER TABLE events ADD COLUMN list_name TEXT NOT NULL DEFAULT 'shopping list'")
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
    if (not isinstance(request, dict) or set(request) not in ({'version','command','item','request_id','human_token'},{'version','command','item','request_id','human_token','list_name'})
            or request['version'] != 'ucii-alexa-shopping-v1' or request['command'] not in {'get','create','add','remove'}
            or not isinstance(request['item'], str) or str(UUID(request['request_id'])) != request['request_id']):
        raise ValueError('Invalid shopping request')
    command = request['command']
    item = ' '.join(request['item'].split()).casefold()
    label = request.get('list_name','Shopping list')
    if not isinstance(label,str) or not label.strip() or len(label)>60 or any(ord(c)<32 for c in label):
        raise ValueError('Supply a short list name')
    label = ' '.join(label.split())
    list_name = label.casefold()
    if (command in {'get','create'} and item) or (command in {'add','remove'} and (not item or len(item)>80 or any(ord(c)<32 for c in request['item']))):
        raise ValueError('Supply one short shopping item')
    action = {'operation':OPERATION, 'resource':'owner-shopping-list', 'subject_identity_id':agent,
              'command':command, 'item':item, 'list_name':list_name}
    # HUMAN was independently resolved by the executor before storage access.
    allowed = command == 'get' or verify(action) is True
    with connect(directory) as db:
        db.execute('BEGIN IMMEDIATE')
        previous = db.execute('SELECT command,item,result,time,list_name FROM events WHERE id=?',(request['request_id'],)).fetchone()
        if previous:
            if previous[:2] != (command,item) or previous[4]!=list_name:
                raise ValueError('Request reference reused for a different edit')
            result, checked_at = previous[2:4]
        elif command == 'get':
            if not db.execute('SELECT 1 FROM lists WHERE name=?',(list_name,)).fetchone():
                raise ValueError('List not found; create it first')
            result, checked_at = 'viewed', datetime.now(timezone.utc).isoformat()
        else:
            allowed = allowed and verify(action) is True
            result = 'blocked'
            if allowed:
                exists = db.execute('SELECT 1 FROM named_items WHERE list_name=? AND name=?',(list_name,item)).fetchone()
                list_exists = db.execute('SELECT 1 FROM lists WHERE name=?',(list_name,)).fetchone()
                if command=='create':
                    if not list_exists and db.execute('SELECT COUNT(*) FROM lists').fetchone()[0]>=12:
                        raise ValueError('Maximum twelve lists')
                    db.execute('INSERT OR IGNORE INTO lists VALUES (?,?)',(list_name,label))
                    result='already_exists' if list_exists else 'created'
                elif not list_exists:
                    raise ValueError('List not found; create it first')
                if command == 'add':
                    if not exists and db.execute('SELECT COUNT(*) FROM named_items WHERE list_name=?',(list_name,)).fetchone()[0] >= 100:
                        raise ValueError('Shopping list is full')
                    db.execute('INSERT OR IGNORE INTO named_items VALUES (?,?)',(list_name,item))
                    result = 'already_present' if exists else 'added'
                elif command=='remove':
                    db.execute('DELETE FROM named_items WHERE list_name=? AND name=?',(list_name,item))
                    result = 'removed' if exists else 'not_present'
            checked_at = datetime.now(timezone.utc).isoformat()
            # Edit and audit record commit together; same request cannot edit twice.
            db.execute('INSERT INTO events (id,command,item,result,time,list_name) VALUES (?,?,?,?,?,?)',(request['request_id'],command,item,result,checked_at,list_name))
        items = [r[0] for r in db.execute('SELECT name FROM named_items WHERE list_name=? ORDER BY name',(list_name,))]
        lists = [r[0] for r in db.execute('SELECT label FROM lists ORDER BY name')]
        stored_label=db.execute('SELECT label FROM lists WHERE name=?',(list_name,)).fetchone()
    return {'operation':OPERATION, 'request_id':request['request_id'], 'result':result,
            'items':items, 'list_name':stored_label[0] if stored_label else label, 'lists':lists, 'checked_at':checked_at, 'purchased':False}

def activity(directory):
    if not (Path(directory)/'shopping.sqlite3').exists():
        return []
    with connect(directory) as db:
        return [{'id':r[0], 'kind':'tool', 'operation':OPERATION,'result':r[1],'time':r[2],'list_name':r[3]}
                for r in db.execute('SELECT events.id,events.result,events.time,COALESCE(lists.label,events.list_name) FROM events LEFT JOIN lists ON lists.name=events.list_name ORDER BY events.time DESC LIMIT 50')]
