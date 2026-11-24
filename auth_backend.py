"""Local account storage and authenticated demo-player API."""
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
import uuid
from datetime import datetime, timezone, timedelta
from http.cookies import SimpleCookie
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('XOT17_DB_PATH', str(ROOT / 'data' / 'private' / 'accounts.sqlite3'))).expanduser().resolve()
SECRET = os.environ.get('AUTH_SECRET', '').encode()
SECRET_FILE = ROOT / 'data' / 'private' / 'session.secret'
SECURE_COOKIE = os.environ.get('XOT17_SECURE_COOKIE') == '1'
COOKIE = 'xot17_session'
TTL = 7 * 24 * 60 * 60
EMAIL = re.compile(r'^[^\s@]{1,64}@[^\s@.]+(?:\.[^\s@.]+)+$')
DUMMY = None
AVATAR_OPTIONS = {'hair': ['spiky','twintails','bob','messy','ponytail','buns','fringe','long'], 'hairColor':['#B86BFF','#00F0FF','#8CFF00','#302143','#664334','#E3AA56','#FA91B8','#FFFFFF'], 'face':['eyes','wink','happy','visor','blush'], 'outfit':['hoodie','tee','jacket','vest'], 'outfitColor':['#8A3FFC','#00AFC2','#598C22','#FF2A85','#2E303E','#EFE5FF'], 'bottom':['shorts','cargo','skirt','sneakers'], 'skin':['#FCE0C7','#E9B38F','#C98359','#95573D','#603826'], 'accessory':['none','headset','horn','bottle','leaf']}
DEFAULT_AVATAR = {key: values[0] for key,values in AVATAR_OPTIONS.items()}

def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db

def init():
    global DUMMY, SECRET
    if not SECRET:
        SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(SECRET_FILE), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            SECRET = SECRET_FILE.read_bytes()
        else:
            SECRET = secrets.token_bytes(32)
            with os.fdopen(fd, 'wb') as f:
                f.write(SECRET)
        if len(SECRET) < 32:
            raise RuntimeError('Stored session secret is invalid; configure AUTH_SECRET or repair session.secret.')
    with connect() as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'USER' CHECK(role IN ('USER','ADMIN')), points INTEGER NOT NULL DEFAULT 0, bottles_recycled INTEGER NOT NULL DEFAULT 0, streak INTEGER NOT NULL DEFAULT 0, last_recycled_day TEXT, created_at TEXT NOT NULL, last_login_at TEXT);
        CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS player_events (id TEXT NOT NULL, user_id TEXT NOT NULL REFERENCES users(id), created_at TEXT NOT NULL, PRIMARY KEY(id,user_id));''')
    with connect() as db:
        if 'avatar_config' not in {row['name'] for row in db.execute('PRAGMA table_info(users)')}:
            db.execute("ALTER TABLE users ADD COLUMN avatar_config TEXT NOT NULL DEFAULT '{}'")
    try: os.chmod(DB, 0o600)
    except OSError: pass
    DUMMY = hash_password('not-a-real-password')

def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
    return 'scrypt$16384$8$1$' + salt.hex() + '$' + digest.hex()

def verify(password, stored):
    try:
        name, n, r, p, salt, expected = stored.split('$')
        if name != 'scrypt': return False
        value = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p), dklen=32)
        return hmac.compare_digest(value, bytes.fromhex(expected))
    except (ValueError, TypeError): return False

def b64(data): return base64.urlsafe_b64encode(data).rstrip(b'=').decode()
def unb64(data): return base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))
def sign(payload):
    head = b64(b'{"alg":"HS256","typ":"JWT"}')
    body = b64(json.dumps(payload, separators=(',', ':')).encode())
    msg = head + '.' + body
    return msg + '.' + b64(hmac.new(SECRET, msg.encode(), hashlib.sha256).digest())
def decode(token):
    try:
        head, body, signature = token.split('.')
        if not hmac.compare_digest(signature, b64(hmac.new(SECRET, (head+'.'+body).encode(), hashlib.sha256).digest())): return None
        if json.loads(unb64(head)) != {'alg':'HS256','typ':'JWT'}: return None
        data = json.loads(unb64(body))
        if not isinstance(data,dict) or not isinstance(data.get('exp'),int) or data['exp'] <= time.time(): return None
        return data
    except (ValueError, TypeError, KeyError, json.JSONDecodeError): return None

def session_cookie(value, max_age=TTL):
    return f'{COOKIE}={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}' + ('; Secure' if SECURE_COOKIE else '')
def issue(db, user_id):
    sid = secrets.token_urlsafe(32); expiry = int(time.time()) + TTL
    db.execute('INSERT INTO sessions VALUES (?,?,?)', (sid, user_id, expiry))
    return sign({'sub':user_id,'sid':sid,'exp':expiry})
def current(handler, db):
    try:
        jar = SimpleCookie(); jar.load(handler.headers.get('Cookie',''))
        token = jar[COOKIE].value if COOKIE in jar else ''
        payload = decode(token)
        if not payload: return None
        return db.execute('SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id WHERE u.id=? AND s.id=? AND s.expires>?', (payload.get('sub'),payload.get('sid'),int(time.time()))).fetchone()
    except (ValueError, KeyError): return None

def safe(row, admin=False):
    value = {'id':row['id'],'email':row['email'],'role':row['role'],'points':row['points'],'bottlesRecycled':row['bottles_recycled'],'streak':row['streak'],'createdAt':row['created_at']}
    try:
        config=json.loads(row['avatar_config'])
        value['avatarConfig']={key: config.get(key) if config.get(key) in choices else DEFAULT_AVATAR[key] for key,choices in AVATAR_OPTIONS.items()} if isinstance(config,dict) else dict(DEFAULT_AVATAR)
    except (ValueError, TypeError): value['avatarConfig']=dict(DEFAULT_AVATAR)
    if admin: value['lastLoginAt'] = row['last_login_at']
    return value

def valid_auth(payload):
    if not isinstance(payload,dict) or set(payload) != {'email','password'}: return None
    email,password = payload['email'],payload['password']
    if not isinstance(email,str) or not isinstance(password,str): return None
    email=email.strip().lower()
    if len(email)>254 or not EMAIL.fullmatch(email) or len(password)<6 or len(password)>256 or len(password.encode())>1024: return None
    return email,password

def handle(handler, method, path, payload=None):
    if path not in ('/api/auth/register','/api/auth/login','/api/auth/logout','/api/auth/me','/api/user/sync','/api/user/avatar','/api/admin/users'): return False
    with connect() as db:
        if path in ('/api/auth/register','/api/auth/login') and method=='POST':
            credentials=valid_auth(payload)
            if not credentials: handler._send_json(400,{'error':'Enter a valid email and a password of 6–256 characters.'}); return True
            email,password=credentials
            if path.endswith('register'):
                hashed=hash_password(password); uid=str(uuid.uuid4()); stamp=now()
                try: db.execute('INSERT INTO users(id,email,password_hash,created_at,last_login_at) VALUES(?,?,?,?,?)',(uid,email,hashed,stamp,stamp))
                except sqlite3.IntegrityError: handler._send_json(409,{'error':'This email is already registered.'}); return True
            else:
                row=db.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
                if not verify(password,row['password_hash'] if row else DUMMY) or not row:
                    handler._send_json(401,{'error':'Invalid email or password.'}); return True
                uid=row['id'];db.execute('UPDATE users SET last_login_at=? WHERE id=?',(now(),uid))
            token=issue(db,uid); row=db.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone();db.commit()
            handler._send_json(201 if path.endswith('register') else 200, safe(row),cookie=session_cookie(token));return True
        if path=='/api/auth/logout' and method=='POST':
            try:
                jar=SimpleCookie();jar.load(handler.headers.get('Cookie',''));data=decode(jar[COOKIE].value) if COOKIE in jar else None
                if data: db.execute('DELETE FROM sessions WHERE id=?',(data.get('sid'),))
            except (ValueError,KeyError): pass
            handler._send_json(200,{'ok':True},cookie=session_cookie('',0));return True
        if path=='/api/auth/me' and method=='GET':
            user=current(handler,db);handler._send_json(200,safe(user) if user else {'user':None});return True
        if path=='/api/admin/users' and method=='GET':
            user=current(handler,db)
            if not user: handler._send_json(401,{'error':'Sign in required.'});return True
            if user['role']!='ADMIN': handler._send_json(403,{'error':'Admin access required.'});return True
            handler._send_json(200,[safe(row,True) for row in db.execute('SELECT * FROM users ORDER BY created_at DESC, id DESC')]);return True
        if path=='/api/user/avatar' and method=='PATCH':
            user=current(handler,db)
            if not user: handler._send_json(401,{'error':'Sign in required.'});return True
            if not isinstance(payload,dict) or set(payload)!={'avatarConfig'} or not isinstance(payload['avatarConfig'],dict):
                handler._send_json(400,{'error':'Invalid avatar.'});return True
            config=payload['avatarConfig']
            if set(config)!=set(AVATAR_OPTIONS) or any(not isinstance(config[key],str) or config[key] not in choices for key,choices in AVATAR_OPTIONS.items()):
                handler._send_json(400,{'error':'Invalid avatar selection.'});return True
            db.execute('UPDATE users SET avatar_config=? WHERE id=?',(json.dumps(config,separators=(',',':')),user['id']))
            row=db.execute('SELECT * FROM users WHERE id=?',(user['id'],)).fetchone();db.commit();handler._send_json(200,safe(row));return True
        if path=='/api/user/sync' and method=='POST':
            user=current(handler,db)
            if not user: handler._send_json(401,{'error':'Sign in required.'});return True
            if not isinstance(payload,dict) or set(payload)!={'action','eventId'} or payload['action'] not in ('bottle','voucher','tree','tote') or not isinstance(payload['eventId'],str) or not re.fullmatch(r'[a-zA-Z0-9-]{16,64}',payload['eventId']):
                handler._send_json(400,{'error':'Invalid action.'});return True
            db.execute('BEGIN IMMEDIATE')
            existing=db.execute('SELECT 1 FROM player_events WHERE id=? AND user_id=?',(payload['eventId'],user['id'])).fetchone()
            if not existing:
                row=db.execute('SELECT * FROM users WHERE id=?',(user['id'],)).fetchone();action=payload['action']
                if action=='bottle':
                    today=datetime.now(timezone.utc).date(); last=row['last_recycled_day']; streak=row['streak'] if last==today.isoformat() else (row['streak']+1 if last==(today-timedelta(days=1)).isoformat() else 1)
                    db.execute('UPDATE users SET points=points+10,bottles_recycled=bottles_recycled+1,streak=?,last_recycled_day=? WHERE id=?',(streak,today.isoformat(),user['id']))
                else:
                    cost={'voucher':200,'tree':400,'tote':600}[action]
                    if row['points']<cost: db.rollback();handler._send_json(409,{'error':'Not enough points.'});return True
                    db.execute('UPDATE users SET points=points-? WHERE id=?',(cost,user['id']))
                db.execute('INSERT INTO player_events VALUES(?,?,?)',(payload['eventId'],user['id'],now()))
            row=db.execute('SELECT * FROM users WHERE id=?',(user['id'],)).fetchone();db.commit();handler._send_json(200,safe(row));return True
        handler._send_json(405,{'error':'Method not allowed.'});return True

def promote(email):
    with connect() as db:
        cur=db.execute("UPDATE users SET role='ADMIN' WHERE email=?",(email.strip().lower(),))
        if cur.rowcount!=1: raise SystemExit('Account not found. Register it first.')
    print('Admin role granted to existing account.')
