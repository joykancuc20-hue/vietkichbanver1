# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import os, sys

# ===== Providers =====
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

def get_client(provider: str):
    p = provider.lower().strip()
    if p == "gemini":
        key = os.getenv("GEMINI_KEY", "")
        if not key: raise HTTPException(400, "Thiếu GEMINI_KEY")
        genai.configure(api_key=key)
        return "gemini"
    if p == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        if not key: raise HTTPException(400, "Thiếu OPENAI_API_KEY")
        return OpenAI(api_key=key)
    if p == "anthropic":
        key = os.getenv("ANTHROPIC_KEY", "")
        if not key: raise HTTPException(400, "Thiếu ANTHROPIC_KEY")
        return Anthropic(api_key=key)
    raise HTTPException(400, "provider không hợp lệ")

def call_model(provider: str, model: str, prompt: str) -> str:
    c = get_client(provider)
    if c == "gemini":
        m = genai.GenerativeModel(f"models/{model}")
        return m.generate_content(prompt).text
    if isinstance(c, OpenAI):
        r = c.chat.completions.create(
            model=model, messages=[{"role":"user","content":prompt}], temperature=0.8
        )
        return r.choices[0].message.content
    if isinstance(c, Anthropic):
        r = c.messages.create(
            model=model, messages=[{"role":"user","content":prompt}], max_tokens=2048
        )
        return r.content[0].text
    raise HTTPException(400, "Không gọi được model")

# ===== App =====
app = FastAPI(title="VietKichBan — One-file")

# ===== Schemas =====
class GenReq(BaseModel):
    provider: str = "gemini"
    model: str = "gemini-2.0-pro"
    params: Dict[str, Any]

# ===== Prompt builders (gọn) =====
def build_create_prompt(p: Dict[str, Any]) -> str:
    idea  = p.get("idea","")
    style = p.get("style","trung tính")
    words = int(p.get("length_words", 800))
    notes = p.get("notes","")
    return f"""Bạn là biên kịch chuyên nghiệp. Viết kịch bản tiếng Việt (~{words} từ), phong cách {style}.
- Mạch có mở đầu/cao trào/kết
- Lời thoại tự nhiên, rõ tên nhân vật
Ý tưởng: {idea}
Ghi chú: {notes}"""

def build_podcast_prompt(p: Dict[str, Any]) -> str:
    topic  = p.get("topic","")
    style  = p.get("style","Trò chuyện thân mật")
    chars  = p.get("characters",[["Host","dẫn dắt"],["Khách","chia sẻ"]])
    roles  = "\n".join([f"- {n}: {d}" for n,d in chars])
    return f"""Viết kịch bản podcast tiếng Việt (mở đầu/thân/kết), phong cách {style}.
Chủ đề: {topic}
Nhân vật:
{roles}
Lời thoại tự nhiên, có cue chuyển cảnh ngắn."""

def build_rewrite_prompt(p: Dict[str, Any]) -> str:
    text   = p.get("text","")
    tone   = p.get("tone","tự nhiên")
    target = p.get("target","ngắn gọn, dễ hiểu")
    return f"""Viết lại đoạn sau bằng tiếng Việt, giữ ý chính, giọng {tone}, mục tiêu {target}.
---
{text}
---"""

# ===== API routes =====
@app.get("/health")
def health():
    return {"ok": True, "routes": ["/", "/api/create", "/api/podcast", "/api/rewrite"]}

@app.post("/api/create")
def api_create(req: GenReq):
    try:
        prompt = build_create_prompt(req.params)
        return {"text": call_model(req.provider, req.model, prompt)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/api/podcast")
def api_podcast(req: GenReq):
    try:
        prompt = build_podcast_prompt(req.params)
        return {"text": call_model(req.provider, req.model, prompt)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/api/rewrite")
def api_rewrite(req: GenReq):
    try:
        prompt = build_rewrite_prompt(req.params)
        return {"text": call_model(req.provider, req.model, prompt)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

# ===== Inline Frontend (no files needed) =====
HTML = """<!doctype html><html lang="vi"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>VietKichBan Web</title>
<style>
:root { --bg:#0b0f19; --card:#121a2b; --bd:#1f2a44; --tx:#eaeefa; --btn:#4b7cf3 }
*{box-sizing:border-box} body{margin:0;font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:var(--tx)}
.wrap{max-width:980px;margin:32px auto;padding:0 16px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:16px;margin:16px 0}
label{display:block;margin:.6rem 0 .25rem}
input,textarea,select{width:100%;padding:.7rem;border-radius:12px;border:1px solid var(--bd);background:#0e1526;color:var(--tx)}
textarea{min-height:120px} button{margin-top:.6rem;padding:.7rem 1rem;border:0;border-radius:12px;background:var(--btn);color:#fff;cursor:pointer}
pre{white-space:pre-wrap;background:#0e1526;border:1px solid var(--bd);border-radius:12px;padding:.7rem;margin-top:.6rem}
</style></head><body>
<main class="wrap">
  <h1>VietKichBan Web</h1>

  <section class="card">
    <h2>📝 Create Script</h2>
    <label>Provider</label>
    <select id="prov1"><option value="gemini">Gemini</option><option value="openai">OpenAI</option><option value="anthropic">Anthropic</option></select>
    <label>Model</label><input id="mod1" value="gemini-2.0-pro"/>
    <label>Ý tưởng</label><textarea id="idea"></textarea>
    <label>Phong cách</label><input id="style" value="trung tính"/>
    <label>Số từ</label><input id="len" type="number" value="800"/>
    <label>Ghi chú</label><textarea id="notes"></textarea>
    <button id="go1">Generate</button><pre id="out1"></pre>
  </section>

  <section class="card">
    <h2>🎙️ Podcast</h2>
    <label>Provider</label>
    <select id="prov2"><option value="gemini">Gemini</option><option value="openai">OpenAI</option><option value="anthropic">Anthropic</option></select>
    <label>Model</label><input id="mod2" value="gemini-2.0-pro"/>
    <label>Chủ đề</label><input id="topic"/>
    <label>Phong cách</label><input id="style2" value="Trò chuyện thân mật"/>
    <label>Nhân vật (mỗi dòng: tên:mô tả)</label><textarea id="chars" placeholder="Host:dẫn dắt&#10;Khách:chia sẻ"></textarea>
    <button id="go2">Generate</button><pre id="out2"></pre>
  </section>

  <section class="card">
    <h2>✍️ Rewrite</h2>
    <label>Provider</label>
    <select id="prov3"><option value="gemini">Gemini</option><option value="openai">OpenAI</option><option value="anthropic">Anthropic</option></select>
    <label>Model</label><input id="mod3" value="gemini-2.0-pro"/>
    <label>Text gốc</label><textarea id="text3"></textarea>
    <label>Tone</label><input id="tone" value="tự nhiên"/>
    <label>Mục tiêu</label><input id="target" value="ngắn gọn, dễ hiểu"/>
    <button id="go3">Generate</button><pre id="out3"></pre>
  </section>
</main>
<script>
async function call(path, payload){
  const res = await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  if(!res.ok){throw new Error(await res.text())}
  return res.json();
}
document.getElementById("go1").onclick = async ()=>{
  const body = {provider:prov1.value, model:mod1.value.trim(), params:{
    idea:idea.value.trim(), style:style.value.trim(), length_words:+len.value||800, notes:notes.value.trim()
  }};
  out1.textContent="Đang xử lý..."; try{ const r = await call("/api/create", body); out1.textContent=r.text||JSON.stringify(r) }catch(e){ out1.textContent="Lỗi: "+e.message }
};
document.getElementById("go2").onclick = async ()=>{
  const chars = charsEl.value.split("\\n").map(s=>s.trim()).filter(Boolean).map(l=>{const a=l.split(":");return [a[0]||"Host",(a.slice(1).join(":")||"").trim()]});
  const body = {provider:prov2.value, model:mod2.value.trim(), params:{
    topic:topic.value.trim(), style:style2.value.trim(), characters:chars
  }};
  out2.textContent="Đang xử lý..."; try{ const r = await call("/api/podcast", body); out2.textContent=r.text||JSON.stringify(r) }catch(e){ out2.textContent="Lỗi: "+e.message }
};
const charsEl = document.getElementById("chars");
document.getElementById("go3").onclick = async ()=>{
  const body = {provider:prov3.value, model:mod3.value.trim(), params:{
    text:text3.value.trim(), tone:tone.value.trim(), target:target.value.trim()
  }};
  out3.textContent="Đang xử lý..."; try{ const r = await call("/api/rewrite", body); out3.textContent=r.text||JSON.stringify(r) }catch(e){ out3.textContent="Lỗi: "+e.message }
};
</script>
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
def ui():
    return HTML

# ===== END =====
