# AI-proposed attack paths (#302)

A local LLM can draft attack paths for an imported model. Every path it drafts is a
proposal: a person accepts or rejects it in Review & Edit (#289, #290), and rates it,
before it counts. Nothing leaves the user's Mac: the engine talks only to an Ollama
server on the same machine. The choices made in building it, and how it was checked, are
in [DL-0082](../design-log/0082-ai-attack-paths/README.md).

## Setup

1. Install Ollama from https://ollama.com/download and open it.
2. In Terminal: `ollama pull qwen3.5:9b` (6.55 GB; for a Mac with 16 GB or more).
3. Start the engine with `tmodel serve --enable-ai`. The app's launcher does not pass
   this switch yet (DL-0078's one switch).

`tmodel ai-status` says whether Ollama is running and the model installed.
`TMODEL_OLLAMA_URL` (a loopback URL only), `TMODEL_AI_MODEL` and `TMODEL_AI_KEEP_ALIVE`
change the defaults. The engine also needs the pinned CWE and CAPEC releases
(`TMODEL_CWE_CATALOG`, `TMODEL_CAPEC_CATALOG`), as the weakness and attack pattern
tables do.

## The routes

Both answer only a loopback Host and the app's origins (or no Origin, for a local
process). `examples/ai-proposals/contract.json` holds every answer below, made by
`tests/test_ai_paths.py` from the real routes for `examples/ai-proposals/imported-example.yaml`.

### `GET /ai/status`

Always `200`. Ask before showing "Suggest attack paths", and again after the user
follows the setup steps.

```json
{
  "enabled": true,
  "ready": false,
  "reason": "model_missing",
  "ollama": {"url": "http://127.0.0.1:11434", "running": true, "version": "0.33.2"},
  "model": {"name": "qwen3.5:9b", "installed": false},
  "setup": ["Install Ollama from https://ollama.com/download and open it.",
            "In Terminal, run: ollama pull qwen3.5:9b"]
}
```

`reason` is `null` when `ready` is true, and otherwise `not_enabled`,
`ollama_not_running` or `model_missing`. `setup` is `null` when ready.

### `POST /ai/attack-paths`

Request: `{"model_text": "<the model as YAML>", "max_paths": 3}`. `max_paths` is 1 to 10
and defaults to 3. Only these two fields are accepted.

`200`:

```json
{
  "model_text": "<the same model with the proposals added>",
  "summary": {"threat_instances": 2, "attack_steps": 4, "attack_paths": 2},
  "paths": [
    {
      "id": "attack-path:ai-exhaust-the-tls-library-s-memory",
      "name": "Exhaust the TLS library's memory",
      "threat": "threat-instance:ai-exhaust-the-tls-library-s-memory",
      "threat_name": "Denial of service through the TLS library",
      "damage": "The service stops answering its clients",
      "steps": [
        {"id": "attack-step:ai-exhaust-the-tls-library-s-memory-1",
         "name": "Open many connections at once",
         "component": "component:example-tls-library",
         "weakness": "weakness:cwe-770", "capec": "CAPEC-125"}
      ]
    }
  ],
  "warnings": ["Overflow the decompressor to run code: every step uses one pattern"],
  "generated_by": {"model": "qwen3.5:9b", "digest": "56671c2ab938",
                   "prompt": "attack-paths/v1", "seconds": 56.2, "attempts": 1}
}
```

A draft takes about a minute on an Apple M3 Pro, so show progress and wait up to five
minutes. Then save `model_text` as the project's next version (for example "AI proposals
(qwen3.5:9b)") and open Review & Edit. The route writes nothing itself.

### Errors

`{"error": {"code", "message", "problems"?, "setup"?}}`, as the other app routes:

| Status | Code | When |
|---|---|---|
| 422 | `validation_error` | no `model_text`, not YAML, not a model, too large, an unknown field, or a bad `max_paths` |
| 422 | `nothing_to_draft` | no component has a weakness the CWE release relates to a CAPEC pattern |
| 422 | `generation_failed` | the model's answers failed the checks three times; `problems` says why |
| 403 | `permission_denied` | a foreign Host or Origin |
| 404 | `not_found` | another `/ai/` path |
| 503 | `not_enabled` | the engine started without `--enable-ai` |
| 503 | `ai_unavailable` | Ollama is not running or the model is missing; `problems` and `setup` say which |
| 503 | `busy` | another draft is running; one runs at a time |
| 504 | `generation_timeout` | no answer within five minutes |
| 500 | `internal_error` | anything else; the answer never holds a path or a traceback |

## What a draft adds to the model

The shape of mvp-01's AI-proposed path, so Review & Edit lists each one:

- a `software_agent` Party for the model (`party:ai-qwen3-5-9b`), once;
- for each path: a `damage_scenario`, a `threat_instance` that realizes it, the
  `attack_steps` chained by `precedes`, and an `attack_path` with `realizes_threat`;
- the CAPEC `attack_patterns` the steps use, when the model has none for them;
- `proposed` Assertions, all by that Party, with the model and its digest in
  `generated_by`: the path `realizes_threat` its threat (the one Review & Edit asks a
  verdict on), the threat `exploits_weakness` each weakness, each step `exploits` its
  weakness, `targets_element` its component and is an `instance_of` its pattern, and each
  weakness is `exploited_by` its pattern when the model did not say so already.

No `attack_feasibility`, rating, risk score or review is written: those are a person's.

## Limits

- The model only picks from the choices the engine offers, so it cannot name a component,
  weakness or pattern that is not in the model and the pinned catalogs; it can still pick
  a pattern that fits the step badly. A person decides.
- A weakness offers at most 8 related patterns: the likeliest and most severe first.
- A component with no vulnerability linked to a weakness, or a weakness that the CWE
  release relates to no pattern (itself or its parents, two levels up), gives no choices.
- The packaged app does not bundle the CAPEC release yet (#294's review).
