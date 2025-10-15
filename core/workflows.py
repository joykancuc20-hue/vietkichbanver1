from .providers import Provider
from .prompts import build_create_prompt, build_podcast_prompt, build_rewrite_prompt

class OmegaLogic:
    def __init__(self, provider: Provider):
        self.p = provider

    def create(self, provider_name: str, model: str, params: dict) -> str:
        prompt = build_create_prompt(params)
        return self.p.call(provider_name, model, prompt)

    def podcast(self, provider_name: str, model: str, params: dict) -> str:
        prompt = build_podcast_prompt(params)
        return self.p.call(provider_name, model, prompt)

    def rewrite(self, provider_name: str, model: str, params: dict) -> str:
        prompt = build_rewrite_prompt(params)
        return self.p.call(provider_name, model, prompt)
