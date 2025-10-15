async function call(path, payload){
  const res = await fetch(`${CONFIG.API_BASE}${path}`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

// CREATE
document.getElementById("btnCreate").onclick = async () => {
  const payload = {
    provider: document.getElementById("providerCreate").value,
    model: document.getElementById("modelCreate").value.trim(),
    params: {
      idea: document.getElementById("idea").value.trim(),
      style: document.getElementById("style").value.trim(),
      length_words: +document.getElementById("length").value || 800,
      notes: document.getElementById("notes").value.trim()
    }
  };
  const out = document.getElementById("outCreate");
  out.textContent = "Đang xử lý...";
  try { out.textContent = (await call("/api/create", payload)).text; }
  catch(e){ out.textContent = "Lỗi: " + e.message; }
};

// PODCAST
document.getElementById("btnPodcast").onclick = async () => {
  const chars = document.getElementById("characters").value
    .split("\n").map(x => x.trim()).filter(Boolean)
    .map(line => {
      const [name,...rest] = line.split(":");
      return [name?.trim()||"Host", (rest.join(":")||"").trim()];
    });

  const payload = {
    provider: document.getElementById("providerPodcast").value,
    model: document.getElementById("modelPodcast").value.trim(),
    params: {
      topic: document.getElementById("topic").value.trim(),
      style: document.getElementById("stylePodcast").value.trim(),
      characters: chars
    }
  };
  const out = document.getElementById("outPodcast");
  out.textContent = "Đang xử lý...";
  try { out.textContent = (await call("/api/podcast", payload)).text; }
  catch(e){ out.textContent = "Lỗi: " + e.message; }
};

// REWRITE
document.getElementById("btnRewrite").onclick = async () => {
  const payload = {
    provider: document.getElementById("providerRewrite").value,
    model: document.getElementById("modelRewrite").value.trim(),
    params: {
      text: document.getElementById("textRewrite").value.trim(),
      tone: document.getElementById("tone").value.trim(),
      target: document.getElementById("target").value.trim(),
    }
  };
  const out = document.getElementById("outRewrite");
  out.textContent = "Đang xử lý...";
  try { out.textContent = (await call("/api/rewrite", payload)).text; }
  catch(e){ out.textContent = "Lỗi: " + e.message; }
};
