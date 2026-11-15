"""Smoke test for the local Ollama server (Stage 1, Step 1).

Run from the repo root:
    uv run python scripts/ollama_smoke.py
    uv run python scripts/ollama_smoke.py --model qwen2.5:3b
"""

import argparse
import sys
import time

import httpx

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:3b"


def ns_to_ms(value: int | None) -> str:
    """Ollama reports durations in nanoseconds; humans prefer milliseconds."""
    if value is None:
        return "n/a"
    return f"{value / 1_000_000:.0f} ms"


def run(base_url: str, model: str) -> int:
    # Separate limits for each phase of the request. A hung model must not hang us forever.
    timeout = httpx.Timeout(connect=5, read=120, write=20, pool=5)

    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        # 1. Is the server up?
        root = client.get("/")
        print(f"[1/3] server reply : {root.text.strip()!r} (HTTP {root.status_code})")

        # 2. Is the model installed?
        tags = client.get("/api/tags").json()
        installed = [item["name"] for item in tags.get("models", [])]
        print(f"[2/3] models found : {installed}")
        if model not in installed:
            print(f"      -> '{model}' is missing. Run: ollama pull {model}")
            return 1

        # 3. Can it answer? Same endpoint our real adapter will use in Step 6.
        started = time.perf_counter()
        response = client.post(
            "/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Reply with the single word: pong"}],
                "stream": False,
                "options": {"temperature": 0, "num_predict": 32},
            },
        )
        wall_seconds = time.perf_counter() - started
        response.raise_for_status()
        body = response.json()

    print(f"[3/3] model reply  : {body['message']['content']!r}")
    print(f"      wall clock   : {wall_seconds:.2f} s")
    print(f"      total        : {ns_to_ms(body.get('total_duration'))}")
    print(f"      model load   : {ns_to_ms(body.get('load_duration'))}")
    print(f"      prompt tokens: {body.get('prompt_eval_count')}")
    print(f"      output tokens: {body.get('eval_count')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test a local Ollama server.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    try:
        return run(args.base_url, args.model)
    except httpx.ConnectError:
        print(f"Cannot connect to Ollama at {args.base_url}. Is it running? Try: ollama serve")
    except httpx.TimeoutException:
        print("Ollama did not answer in time. The first call after boot can be slow; try again.")
    except httpx.HTTPStatusError as exc:
        print(f"Ollama returned HTTP {exc.response.status_code}: {exc.response.text[:300]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())