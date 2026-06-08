Status: #library
Tags: #framework #AI-infra #compute

---

# Agentic AI Shifts the Compute *Mix* Toward CPU — Not Away From GPU

The "CPUs are back" narrative is real but easily misread. The right framing is **mix shift, not substitution**: agentic workloads have a different compute profile than chat-style inference, and CPU's share of the inference pie grows as agent step-counts grow — even while absolute GPU demand keeps compounding.

## The mechanism

A chat completion is one model call: GPU-bound, end-to-end. An agent loop is N model calls plus ~N rounds of tool-calling, parsing, retrieval, routing, and state management. The model calls are GPU; the glue code between them is CPU. As step-counts go from 1 to 10 to 50+ per query, CPU's share of per-query compute rises mechanically.

Hyperscaler procurement confirms the shift is large enough to warrant first-party silicon at scale: AMZN's Graviton (committed to in the "hundreds of thousands of cores" by at least one top-5 customer for agentic inference + orchestration), GOOGL's Axion, and MSFT's Cobalt are all in-house ARM CPUs aimed at the inference-orchestration layer.

## Why ARM matters

Graviton/Axion/Cobalt are all ARM, which delivers materially better perf/watt than x86 at hyperscale. When the binding constraint is power (see [[AI Energy Thesis]]), CPU efficiency gains are substrate gains — the same megawatt produces more useful agentic compute. ARM's mix-shift advantage compounds with the power thesis rather than competing with it.

## Implications by sleeve

- **Hyperscaler first-party silicon is the moat.** AMZN, GOOGL, MSFT each capture orchestration-layer margin via owned ARM silicon, on top of GPU/accelerator capacity. Sharpens [[orchestration-vs-substrate]] in their favor — they're structurally long both sides of the stack.
- **Bearish for x86 hyperscaler share.** INTC and AMD lose CPU sockets in the inference-orchestration layer to first-party ARM. Doesn't kill them — enterprise on-prem and consumer remain — but the highest-growth slice of CPU demand is being internalized.
- **Neutral for NVDA.** Training stays GPU; per-step inference stays GPU. Absolute GPU demand keeps compounding even as CPU's *share* grows. The mix shift expands the total inference pie rather than eating the GPU TAM.
- **Neutral-to-positive for substrate picks-and-shovels (IREN, CORZ, CRWV, BE).** A CPU rack still needs power, cooling, and DC capacity. ARM efficiency means more compute per MW, but the MW is still rented — the "power is the binding constraint" framing is reinforced.

## What would invalidate this framing

- Agentic workloads stall as a category — if real-world agents underperform chat assistants on ROI, the step-count growth that drives CPU share never materializes.
- ARM's efficiency edge gets eroded by next-gen x86. Possible but slow — perf/watt gaps this size take 2–3 generations to close.
- A breakthrough in "fused" inference where multi-step reasoning happens inside one GPU forward pass would re-collapse the agent loop into GPU-bound territory. Watch for it; don't expect it near-term.

## What this is *not* saying

This is **not** "CPUs replace GPUs" or "buy CPU stocks, sell GPU stocks" — that's the Twitter version. The investable claim is narrower: hyperscalers with first-party ARM silicon capture more of the orchestration-layer margin in the agentic build-out, and the cleanest expression of that is a hyperscaler that owns both the orchestration silicon and a training/inference accelerator at scale.

---
# References
- [[orchestration-vs-substrate]] — first-party ARM silicon = orchestration-layer margin capture
- [[AI Energy Thesis]] — perf-per-watt is a substrate gain, not a substitution threat
- [[ai-infra-thesis-kill-switches]] — none of the three kill-switches is tripped by the CPU mix shift
