"""A local LLM through Ollama, for the AI proposals (#302, DL-0082).

The engine talks only to an Ollama server on this machine: the URL must name a loopback
host, so a model's prompt (a product's components, CVEs and CWEs) never leaves it. Two
calls are used, both over Ollama's HTTP API:

- `status()`: is Ollama running, and is the model installed (`GET /api/version`,
  `GET /api/tags`)? It never raises; it says what is missing.
- `chat_json(prompt, schema)`: one chat turn whose answer must fit `schema`, a JSON
  Schema that Ollama's `format` enforces while the model writes (`POST /api/chat`). The
  temperature is 0 and the seed fixed, so a draft can be repeated.

The model is unloaded after each answer (`keep_alive: 0`): a 9B model holds about 7 GB
while it is loaded, which the user's other apps need back. `TMODEL_OLLAMA_URL`,
`TMODEL_AI_MODEL` and `TMODEL_AI_KEEP_ALIVE` change the defaults.
"""

from __future__ import annotations

import ipaddress
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

DEFAULT_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3.5:9b"
DEFAULT_SEED = 7
DEFAULT_CONTEXT = 8192  # tokens: the prompt (about 4,000) and the answer, with room
DEFAULT_ANSWER = 4096  # tokens the answer may use
STATUS_TIMEOUT_S = 3.0
SETUP_STEPS = (
    "Install Ollama from https://ollama.com/download and open it.",
    "In Terminal, run: ollama pull {model}",
)


class LlmError(Exception):
    """The local LLM could not answer. `code` is one of ollama_not_running,
    model_missing, generation_timeout or bad_answer."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _loopback_url(url: str) -> str:
    parts = urlsplit(url)
    host = parts.hostname or ""
    try:
        loopback = host == "localhost" or ipaddress.ip_address(host).is_loopback
    except ValueError:
        loopback = False
    if parts.scheme != "http" or not loopback or parts.path not in ("", "/") or parts.query:
        raise ValueError(f"the Ollama URL must be http:// on this machine, not {url!r}")
    return url.rstrip("/")


@dataclass
class Ollama:
    """An Ollama server on this machine and the model to ask."""

    url: str = field(default_factory=lambda: os.environ.get("TMODEL_OLLAMA_URL", DEFAULT_URL))
    model: str = field(default_factory=lambda: os.environ.get("TMODEL_AI_MODEL", DEFAULT_MODEL))
    timeout: float = 300.0  # seconds for one answer
    keep_alive: str = field(default_factory=lambda: os.environ.get("TMODEL_AI_KEEP_ALIVE", "0"))

    def __post_init__(self) -> None:
        self.url = _loopback_url(self.url)

    def _call(self, path: str, body: dict[str, Any] | None, timeout: float) -> dict[str, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.url + path,
            data=data,
            method="GET" if body is None else "POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                answer = json.loads(response.read())
        except TimeoutError as exc:
            raise LlmError(
                "generation_timeout", f"Ollama did not answer within {timeout:g} s."
            ) from exc
        except urllib.error.HTTPError as exc:
            detail = exc.read()[:300].decode("utf-8", "replace")
            if exc.code == 404 and "not found" in detail:
                raise LlmError("model_missing", f"Ollama has no model {self.model!r}.") from exc
            raise LlmError("bad_answer", f"Ollama answered {exc.code}: {detail}") from exc
        except (urllib.error.URLError, ConnectionError, OSError) as exc:
            if isinstance(getattr(exc, "reason", None), TimeoutError):
                raise LlmError(
                    "generation_timeout", f"Ollama did not answer within {timeout:g} s."
                ) from exc
            raise LlmError("ollama_not_running", f"Ollama is not running at {self.url}.") from exc
        except ValueError as exc:
            raise LlmError("bad_answer", "Ollama's answer was not JSON.") from exc
        if not isinstance(answer, dict):
            raise LlmError("bad_answer", "Ollama's answer was not a JSON object.")
        return answer

    def setup_steps(self) -> list[str]:
        return [step.format(model=self.model) for step in SETUP_STEPS]

    def status(self) -> dict[str, Any]:
        """Whether a draft can run now, and if not, why. Never raises."""
        model: dict[str, Any] = {"name": self.model, "installed": False}
        out: dict[str, Any] = {
            "ready": False,
            "reason": "ollama_not_running",
            "ollama": {"url": self.url, "running": False, "version": None},
            "model": model,
        }
        try:
            version = self._call("/api/version", None, STATUS_TIMEOUT_S)
            tags = self._call("/api/tags", None, STATUS_TIMEOUT_S)
        except LlmError:
            return out
        out["ollama"].update(running=True, version=version.get("version"))
        for entry in tags.get("models") or []:
            if isinstance(entry, dict) and entry.get("name") in (
                self.model,
                f"{self.model}:latest",
            ):
                model.update(
                    installed=True,
                    digest=str(entry.get("digest") or ""),
                    size_bytes=entry.get("size"),
                )
                break
        out["ready"] = model["installed"]
        out["reason"] = None if model["installed"] else "model_missing"
        return out

    def chat_json(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        seed: int = DEFAULT_SEED,
        context: int = DEFAULT_CONTEXT,
        answer_tokens: int = DEFAULT_ANSWER,
    ) -> tuple[Any, dict[str, Any]]:
        """The model's answer to `prompt`, parsed, and what the run took."""
        body = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": schema,
            "keep_alive": self.keep_alive,
            "options": {
                "temperature": 0,
                "seed": seed,
                "num_ctx": context,
                "num_predict": answer_tokens,
            },
            "messages": [{"role": "user", "content": prompt}],
        }
        started = time.monotonic()
        reply = self._call("/api/chat", body, self.timeout)
        stats = {
            "seconds": round(time.monotonic() - started, 1),
            "prompt_tokens": reply.get("prompt_eval_count"),
            "answer_tokens": reply.get("eval_count"),
            "done_reason": reply.get("done_reason"),
        }
        if reply.get("done_reason") == "length":
            raise LlmError("bad_answer", "The answer ran past its length limit.")
        content = (reply.get("message") or {}).get("content")
        if not isinstance(content, str):
            raise LlmError("bad_answer", "Ollama's answer had no message.")
        try:
            return json.loads(content), stats
        except ValueError as exc:
            raise LlmError("bad_answer", "The model's answer was not JSON.") from exc
