# design-log/

The AI-assisted design record. This project claims AI-assisted development as
part of its method; that claim is only credible if it is **instrumented**.

One directory per entry: `NNNN-slug/`. Each entry records:

- **the question asked** of the agent,
- **what it produced** (spec text, schema, mappings, vectors, code),
- **what a human accepted**, and
- **what a human rejected, and why** — the rejections are the evidence.

Write the entry **in the same change** that produced the artifact, never
reconstructed later. A design-log entry written a week after the fact is
permanently degraded.
