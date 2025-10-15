from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os, json, threading, sys

from core.providers import Provider
from core.workflows import OmegaLogic
from core.youtube import get_transcript
from core.utils import log_error
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# ... app = FastAPI(...) đã có ở trên

# Phục vụ UI từ thư mục frontend/
app.mount("/app", StaticFiles(directory="frontend", html=True), name="app")

# Cho / tự chuyển vào UI (nếu muốn)
@app.get("/")
def root():
    return RedirectResponse(url="/app/")

app = FastAPI(title="VietKichBan Web API")

CONFIG_PATH = "config.json"
CONFIG_LOCK = threading.Lock()

def read_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def write_config(cfg: dict):
    with CONFIG_LOCK:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

def get_api_key(provider: str):
    cfg = read_config()
    api_keys = cfg.get("api_keys", {})
    last_idx = cfg.get("last_used_indices", {})
    provider = provider.lower().strip()
    keys = api_keys.get(provider, [])
    if not keys:
        env_map = {"gemini":"GEMINI_KEY", "openai":"OPENAI_API_KEY", "anthropic":"ANTHROPIC_KEY"}
        return os.getenv(env_map.get(provider, ""), "")
    i = last_idx.get(provider, 0) % len(keys)
    key = keys[i]
    last_idx[provider] = (i + 1) % len(keys)
    cfg["last_used_indices"] = last_idx
    write_config(cfg)
    return key

def refresh_provider():
    global prov, logic
    prov = Provider(
        gemini_key=get_api_key("gemini"),
        openai_key=get_api_key("openai"),
        anthropic_key=get_api_key("anthropic"),
    )
    logic = OmegaLogic(prov)

# init
prov = None
logic = None
refresh_provider()

class GenReq(BaseModel):
    provider: str = "gemini"
    model: str = "gemini-2.0-pro"
    params: Dict[str, Any]

class KeyIn(BaseModel):
    provider: str
    api_key: str

class YTReq(BaseModel):
    url: str
    lang: str = "vi"

@app.get("/")
def health():
    return {"ok": True, "routes": ["/api/create","/api/podcast","/api/rewrite","/api/youtube/transcript","/api/keys"]}

@app.post("/api/create")
def api_create(req: GenReq):
    try:
        return {"text": logic.create(req.provider, req.model, req.params)}
    except Exception as e:
        log_error(sys.exc_info(), context="/api/create")
        raise HTTPException(400, str(e))

@app.post("/api/podcast")
def api_podcast(req: GenReq):
    try:
        return {"text": logic.podcast(req.provider, req.model, req.params)}
    except Exception as e:
        log_error(sys.exc_info(), context="/api/podcast")
        raise HTTPException(400, str(e))

@app.post("/api/rewrite")
def api_rewrite(req: GenReq):
    try:
        return {"text": logic.rewrite(req.provider, req.model, req.params)}
    except Exception as e:
        log_error(sys.exc_info(), context="/api/rewrite")
        raise HTTPException(400, str(e))

@app.post("/api/youtube/transcript")
def api_youtube(req: YTReq):
    try:
        text = get_transcript(req.url, req.lang)
        return {"text": text}
    except Exception as e:
        log_error(sys.exc_info(), context="/api/youtube/transcript")
        raise HTTPException(400, str(e))

# ===== BYOK: người dùng tự thêm key =====
@app.get("/api/keys")
def get_keys():
    cfg = read_config()
    api_keys = cfg.get("api_keys", {"gemini":[],"openai":[],"anthropic":[]})
    masked = {}
    for prov_name, arr in api_keys.items():
        masked[prov_name] = [("****"+k[-4:]) if len(k)>=8 else "****" for k in arr]
    return {"keys": masked, "last_used_indices": cfg.get("last_used_indices", {})}

@app.post("/api/keys")
def save_key(k: KeyIn):
    cfg = read_config()
    api_keys = cfg.get("api_keys", {})
    prov_name = k.provider.lower().strip()
    if prov_name not in api_keys: 
        api_keys[prov_name] = []
    if k.api_key and k.api_key not in api_keys[prov_name]:
        api_keys[prov_name].append(k.api_key)
    cfg["api_keys"] = api_keys
    if "last_used_indices" not in cfg: 
        cfg["last_used_indices"] = {"gemini":0,"openai":0,"anthropic":0}
    write_config(cfg)
    refresh_provider()
    return {"ok": True}

@app.delete("/api/keys")
def delete_key(provider: str, last4: str = ""):
    cfg = read_config()
    api_keys = cfg.get("api_keys", {})
    prov_name = provider.lower().strip()
    if prov_name not in api_keys:
        return {"ok": True}
    if last4:
        api_keys[prov_name] = [k for k in api_keys[prov_name] if not k.endswith(last4)]
    else:
        api_keys[prov_name] = []
    cfg["api_keys"] = api_keys
    write_config(cfg)
    refresh_provider()
    return {"ok": True}
