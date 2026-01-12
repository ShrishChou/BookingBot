import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()  # loads .env from repo root by default

def _must(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required env var: {name}. Put it in .env.")
    return v

@dataclass(frozen=True)
class Config:
    username: str
    password: str
    headless: bool

def get_config() -> Config:
    headless_raw = os.getenv("CLUBAUTO_HEADLESS", "true").strip().lower()
    headless = headless_raw in ("1", "true", "yes", "y")
    return Config(
        username=_must("CLUBAUTO_USERNAME"),
        password=_must("CLUBAUTO_PASSWORD"),
        headless=headless,
    )
