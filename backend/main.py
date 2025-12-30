import os, json, asyncio, shutil, logging
from typing import List, Dict, Optional
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import docker

STACKS_DIR = "/stacks"
GLOBAL_ENV_PATH = "/stacks/.env"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DockMaster")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_docker_client():
    try: return docker.from_env()
    except: raise HTTPException(status_code=503, detail="Docker Unavailable")

class ContainerMeta(BaseModel):
    id: str
    name: str
    status: str
    state: str
    icon: str = ""
    labels: Dict[str, str] = {}
    ports: Dict[str, Optional[List[Dict[str, str]]]] = {}

class Stack(BaseModel):
    name: str
    status: str
    containers: List[ContainerMeta]

class FileUpdate(BaseModel):
    content: str
    filename: str

@app.get("/api/config")
def get_config():
    return {
        "proxy_provider": os.getenv("PROXY_PROVIDER", "traefik").lower(),
        "docker_host_ip": os.getenv("DOCKER_HOST_IP", "")
    }

@app.get("/api/stacks")
def list_stacks():
    client = get_docker_client()
    if not os.path.exists(STACKS_DIR): return []
    stacks = []
    for d in os.listdir(STACKS_DIR):
        full_path = os.path.join(STACKS_DIR, d)
        if os.path.isdir(full_path) and not d.startswith('.'):
            try:
                conts = client.containers.list(all=True, filters={"label": f"com.docker.compose.project={d}"})
                if not conts: conts = client.containers.list(all=True, filters={"label": f"com.docker.compose.project={d.lower()}"})
            except: conts = []
            
            sidecar = {}
            try:
                with open(os.path.join(full_path, ".dockmaster.json"), 'r') as f: sidecar = json.load(f)
            except: pass

            status = "Stopped"
            if conts:
                if any(c.status == 'running' for c in conts):
                    status = "Running" if all(c.status == 'running' for c in conts) else "Partial"
            
            container_list = [ContainerMeta(
                id=c.id, name=c.name, status=c.status, state=c.attrs['State']['Status'],
                icon=sidecar.get('icons', {}).get(c.name, ""),
                labels=c.labels, ports=c.attrs['NetworkSettings']['Ports']
            ) for c in conts]
            stacks.append(Stack(name=d, status=status, containers=container_list))
    return sorted(stacks, key=lambda x: x.name)

@app.get("/api/stacks/stats")
async def get_all_stats():
    stats_data = {}
    try:
        containers = client.containers.list()
        for container in containers:
            # We get a single snapshot of stats
            s = container.stats(stream=False)
            
            # CPU Calculation
            cpu_delta = s["cpu_stats"]["cpu_usage"]["total_usage"] - s["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = s["cpu_stats"]["system_cpu_usage"] - s["precpu_stats"]["system_cpu_usage"]
            cpu_percent = 0.0
            if system_delta > 0.0 and cpu_delta > 0.0:
                cpu_percent = (cpu_delta / system_delta) * len(s["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100.0

            # Memory Calculation
            mem_usage = s["memory_stats"]["usage"]
            mem_limit = s["memory_stats"]["limit"]
            mem_percent = (mem_usage / mem_limit) * 100.0

            stats_data[container.id] = {
                "cpu": round(cpu_percent, 1),
                "mem": round(mem_percent, 1)
            }
        return stats_data
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/stack/create")
async def create_stack(data: dict):
    name = data.get("name", "").strip().replace(" ", "_")
    stack_path = os.path.join(STACKS_DIR, name)
    os.makedirs(stack_path, exist_ok=True)
    with open(os.path.join(stack_path, "docker-compose.yml"), 'w') as f: f.write("services:\n  ")
    return {"status": "success", "name": name}

@app.delete("/api/stack/{stack_name}")
def delete_stack(stack_name: str):
    client = get_docker_client()
    try:
        conts = client.containers.list(all=True, filters={"label": f"com.docker.compose.project={stack_name}"})
        for c in conts: c.remove(force=True)
        shutil.rmtree(os.path.join(STACKS_DIR, stack_name))
        return {"status": "success"}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stack/{stack_name}/file/{filename}")
def get_stack_file(stack_name: str, filename: str):
    path = GLOBAL_ENV_PATH if filename == "global.env" else os.path.join(STACKS_DIR, stack_name, filename)
    if not os.path.exists(path): return {"content": ""}
    with open(path, 'r') as f: return {"content": f.read()}

@app.post("/api/stack/{stack_name}/file")
def save_stack_file(stack_name: str, data: FileUpdate):
    path = GLOBAL_ENV_PATH if data.filename == "global.env" else os.path.join(STACKS_DIR, stack_name, data.filename)
    with open(path, 'w') as f: f.write(data.content)
    return {"status": "success"}

@app.post("/api/container/{container_id}/{action}")
def container_action(container_id: str, action: str):
    client = get_docker_client()
    container = client.containers.get(container_id)
    if action == "start": container.start()
    elif action == "stop": container.stop()
    elif action == "restart": container.restart()
    return {"status": "success"}

@app.get("/api/container/{container_id}/logs")
def get_container_logs(container_id: str):
    try:
        container = get_docker_client().containers.get(container_id)
        return {"logs": container.logs(tail=200).decode('utf-8')}
    except Exception as e: return {"logs": str(e)}

@app.post("/api/stack/{stack_name}/metadata")
def save_metadata(stack_name: str, data: dict):
    path = os.path.join(STACKS_DIR, stack_name, ".dockmaster.json")
    existing = {}
    if os.path.exists(path):
        with open(path, 'r') as f: existing = json.load(f)
    existing.setdefault('icons', {}).update(data.get('icons', {}))
    with open(path, 'w') as f: json.dump(existing, f)
    return {"status": "success"}

@app.websocket("/ws/deploy/{stack_name}")
async def deploy_endpoint(websocket: WebSocket, stack_name: str):
    await websocket.accept()
    try:
        cmd = f"env $(cat {GLOBAL_ENV_PATH} | xargs) docker compose up -d --remove-orphans --force-recreate"
        proc = await asyncio.create_subprocess_shell(cmd, cwd=os.path.join(STACKS_DIR, stack_name), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        while True:
            line = await proc.stdout.readline()
            if not line: break
            await websocket.send_text(line.decode().replace('\n', '\r\n'))
    finally: await websocket.send_text("\r\n--- FINISHED ---")

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5555)
