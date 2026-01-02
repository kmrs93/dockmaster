import os, json, asyncio, shutil, logging, psutil, threading, queue, bcrypt
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
import docker

# --- CONFIG ---
STACKS_DIR = os.getenv("STACKS_ROOT", "/app/projects")
GLOBAL_ENV_PATH = os.path.join(STACKS_DIR, ".env")
CONFIG_DIR = "/app/config"
METADATA_FILE = os.path.join(CONFIG_DIR, "metadata.json")
SECRET_KEY = os.getenv("JWT_SECRET", "dockmaster_32_bit_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
PWD_HASH = os.getenv("DOCKMASTER_PASSWORD_HASH")

os.makedirs(CONFIG_DIR, exist_ok=True)
PROXY_PROVIDER = os.getenv("PROXY_PROVIDER", "caddy").lower()
DOCKER_HOST_IP = os.getenv("DOCKER_HOST_IP", "localhost")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DockMaster")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- HELPERS ---
def get_metadata():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_metadata(data):
    with open(METADATA_FILE, "w") as f: json.dump(data, f, indent=4)

def resolve_url(container, manual_url=None):
    if manual_url: return manual_url
    labels = container.labels
    if PROXY_PROVIDER == "caddy":
        host = labels.get("caddy") or labels.get("caddy.reverse_proxy")
        if host: return f"https://{host.split(',')[0].strip().replace('http://', '').replace('https://', '')}"
    ports = container.attrs['NetworkSettings']['Ports']
    for p in ports:
        if ports[p]:
            hp = ports[p][0].get("HostPort")
            if hp: return f"http://{DOCKER_HOST_IP}:{hp}"
    return None

def verify_token(token: str):
    try: return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    except JWTError: return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    u = verify_token(token)
    if not u: raise HTTPException(status_code=401)
    return u

def get_docker_client():
    return docker.from_env()

# --- MODELS ---
class ContainerMeta(BaseModel):
    id: str; name: str; display_name: str = ""; status: str; state: str; 
    icon: str = ""; url: Optional[str] = None; ports: Dict = {}; hidden: bool = False

class Stack(BaseModel):
    name: str; status: str; containers: List[ContainerMeta]; hidden: bool = False

class FileUpdate(BaseModel):
    content: str; filename: str

# --- ROUTES ---
@app.post("/api/login")
async def login(f: OAuth2PasswordRequestForm = Depends()):
    if not PWD_HASH or not bcrypt.checkpw(f.password.encode(), PWD_HASH.encode()):
        raise HTTPException(status_code=401)
    return {"access_token": jwt.encode({"sub":"admin", "exp": datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM), "token_type": "bearer"}

@app.get("/api/system/stats")
def get_stats(u: str = Depends(get_current_user)):
    t = 0
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f: t = int(f.read())/1000
    except: pass
    return {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "disk": psutil.disk_usage('/').percent, "temp": round(t, 1)}

@app.get("/api/stacks")
def list_stacks(u: str = Depends(get_current_user)):
    client = get_docker_client()
    meta = get_metadata()
    all_conts = client.containers.list(all=True)
    pmap = {}
    for c in all_conts:
        p = c.labels.get("com.docker.compose.project")
        if p:
            if p not in pmap: pmap[p] = []
            pmap[p].append(c)

    res = []
    if not os.path.exists(STACKS_DIR): return []
    for d in os.listdir(STACKS_DIR):
        if os.path.isdir(os.path.join(STACKS_DIR, d)) and not d.startswith('.'):
            conts = pmap.get(d) or pmap.get(d.lower(), [])
            
            clist = []
            for c in conts:
                c_meta = meta.get(c.id, {})
                clist.append(ContainerMeta(
                    id=c.id, 
                    name=c.name, 
                    display_name=c_meta.get("display_name", c.name), 
                    status=c.status, 
                    state=c.attrs['State']['Status'], 
                    icon=c_meta.get("icon", ""), 
                    url=resolve_url(c, c_meta.get("url")), 
                    ports=c.attrs['NetworkSettings']['Ports'],
                    hidden=c_meta.get("hidden", False) # Load hidden state
                ))
            
            status = "Stopped"
            if conts: status = "Running" if all(c.status=='running' for c in conts) else "Partial"
            
            # Load stack hidden state using folder name as key
            stack_hidden = meta.get(f"stack:{d}", {}).get("hidden", False)
            res.append(Stack(name=d, status=status, containers=clist, hidden=stack_hidden))
            
    return sorted(res, key=lambda x: x.name)

@app.post("/api/stack/create")
async def create_stack(data: dict = Body(...), u: str = Depends(get_current_user)):
    name = data.get("name", "").strip().replace(" ", "_")
    if not name: raise HTTPException(status_code=400, detail="Name required")
    path = os.path.join(STACKS_DIR, name)
    os.makedirs(path, exist_ok=True)
    compose = os.path.join(path, "docker-compose.yml")
    if not os.path.exists(compose):
        with open(compose, 'w') as f: f.write("services:\n  ")
    return {"status": "success"}

@app.delete("/api/stack/{sn}")
def delete_stack(sn: str, u: str = Depends(get_current_user)):
    path = os.path.join(STACKS_DIR, sn)
    if os.path.exists(path):
        shutil.rmtree(path)
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Stack not found")

# --- UPDATED METADATA ENDPOINTS ---
@app.post("/api/container/{cid}/metadata")
async def set_container_meta(cid: str, data: dict, u: str = Depends(get_current_user)):
    m = get_metadata()
    if cid not in m: m[cid] = {}
    m[cid].update(data) # Update only provided fields (display_name, icon, hidden, etc.)
    save_metadata(m)
    return {"status": "success"}

@app.post("/api/stack/{sn}/metadata")
async def set_stack_meta(sn: str, data: dict, u: str = Depends(get_current_user)):
    m = get_metadata()
    key = f"stack:{sn}"
    if key not in m: m[key] = {}
    m[key].update(data)
    save_metadata(m)
    return {"status": "success"}

@app.get("/api/stack/{sn}/file/{fn}")
def get_file(sn: str, fn: str, u: str = Depends(get_current_user)):
    p = GLOBAL_ENV_PATH if fn == "global.env" else os.path.join(STACKS_DIR, sn, fn)
    content = ""
    if os.path.exists(p):
        with open(p, 'r') as f: content = f.read()
    return {"content": content}

@app.post("/api/stack/{sn}/file")
def save_file(sn: str, data: FileUpdate, u: str = Depends(get_current_user)):
    p = GLOBAL_ENV_PATH if data.filename == "global.env" else os.path.join(STACKS_DIR, sn, data.filename)
    with open(p, 'w') as f: f.write(data.content)
    return {"status": "success"}

@app.post("/api/container/{cid}/{act}")
def cont_act(cid: str, act: str, u: str = Depends(get_current_user)):
    c = get_docker_client().containers.get(cid)
    getattr(c, act)()
    return {"status": "success"}

# --- WEBSOCKETS ---
@app.websocket("/ws/logs/{cid}")
async def ws_logs(websocket: WebSocket, cid: str, token: str = Query(None)):
    if not token or not verify_token(token):
        await websocket.close(code=4003); return
    await websocket.accept()
    stop_evt = threading.Event()
    loop = asyncio.get_event_loop()

    def stream_worker():
        try:
            container = get_docker_client().containers.get(cid)
            for line in container.logs(stream=True, tail=200, follow=True):
                if stop_evt.is_set(): break
                msg = line.decode('utf-8', errors='replace').replace('\n', '\r\n')
                asyncio.run_coroutine_threadsafe(websocket.send_text(msg), loop)
        except: pass

    t = threading.Thread(target=stream_worker, daemon=True)
    t.start()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "QUIT": break
    except: pass
    finally:
        stop_evt.set()
        await websocket.close()

@app.websocket("/ws/deploy/{sn}")
async def ws_deploy(websocket: WebSocket, sn: str, token: str = Query(None)):
    if not token or not verify_token(token):
        await websocket.close(code=4003); return
    await websocket.accept()
    cmd = f"docker compose --env-file {GLOBAL_ENV_PATH} up -d --remove-orphans --force-recreate"
    p = await asyncio.create_subprocess_shell(cmd, cwd=os.path.join(STACKS_DIR, sn), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    while True:
        line = await p.stdout.readline()
        if not line: break
        await websocket.send_text(line.decode().replace('\n', '\r\n'))
    await websocket.send_text("\r\n--- FINISHED ---")
    await websocket.close()

@app.websocket("/ws/down/{sn}")
async def ws_down(websocket: WebSocket, sn: str, token: str = Query(None)):
    if not token or not verify_token(token):
        await websocket.close(code=4003); return
    await websocket.accept()
    cmd = f"docker compose --env-file {GLOBAL_ENV_PATH} down"
    p = await asyncio.create_subprocess_shell(cmd, cwd=os.path.join(STACKS_DIR, sn), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    while True:
        line = await p.stdout.readline()
        if not line: break
        await websocket.send_text(line.decode().replace('\n', '\r\n'))
    await websocket.send_text("\r\n--- FINISHED ---")
    await websocket.close()

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5555)
