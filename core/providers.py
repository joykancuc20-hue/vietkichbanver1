import os
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

class Provider:
    def __init__(self, gemini_key=None, openai_key=None, anthropic_key=None):
        self.gemini_key    = gemini_key    or os.getenv("GEMINI_KEY", "")
        self.openai_key    = openai_key    or os.getenv("OPENAI_API_KEY", "")
        self.anthropic_key = anthropic_key or os.getenv("ANTHROPIC_KEY", "")

        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        self._openai    = OpenAI(api_key=self.openai_key) if self.openai_key else None
        self._anthropic = Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None

    def call(self, provider: str, model: str, prompt: str) -> str:
        provider = provider.lower().strip()
        if provider == "gemini":
            m = genai.GenerativeModel(f"models/{model}")
            out = m.generate_content(prompt)
            return out.text
        if provider == "openai":
            if not self._openai: raise RuntimeError("OPENAI_API_KEY not set")
            res = self._openai.chat.completions.create(
                model=model, messages=[{"role":"user","content":prompt}], temperature=0.8
            )
            return res.choices[0].message.content
        if provider == "anthropic":
            if not self._anthropic: raise RuntimeError("ANTHROPIC_KEY not set")
            res = self._anthropic.messages.create(
                model=model, messages=[{"role":"user","content":prompt}], max_tokens=2048
            )
            return res.content[0].text
        raise ValueError("Unknown provider: " + provider)
