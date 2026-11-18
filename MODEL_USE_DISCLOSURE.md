# Model-use disclosure

**Status:** this file records what can and cannot be established about the AI
models used in this project. It does not add, remove, or change any analysis
result. It is a documentation artifact, written 2026-11-18.

## 1. Why this file exists

`AGENTS.md` rules 5 and 14 require the prompt, output, and exact model
identifier of every model call to be logged, and `plan.md` §5 repeats that
requirement. Before this file, the repository did not satisfy it for the AI
agent: no committed artifact recorded the agent's model name, provider,
version, prompt, or call timestamp. `results/analysis/model_log.md` records
**statistical** procedures (z-tests, Welch tests, OLS/HC1, bootstrap), not the
AI model.

This file therefore separates three tiers: what is supported by preserved
evidence, what the execution environment reported, and what is unknown or
unrecoverable. Nothing in the unknown tier is guessed.

## 2. Tier 1 — model identities supported by preserved evidence

**None.**

Before this disclosure file was added, no committed file contained an AI model
name, provider identifier, version, prompt, prompt hash, API response, or
model-call timestamp. A search of the analysis artifacts and Git history
returns only:

- `AGENTS.md` rules 5 and 14 (the requirement itself);
- `plan.md` §5 (the promise to log model calls);
- `results/analysis/model_log.md` (records of *statistical* models only).

"Supported by preserved evidence" here means a reviewer can inspect a
repository artifact and verify the identity. No such artifact exists for the
AI agent. Claims about "the model" therefore cannot be grounded in the
repository alone.

## 3. Tier 2 — model identity reported by the execution environment

The agent runtime that produced this repository's final documentation
reported the following identifier to the agent itself:

| Field | Reported value | Evidential status |
|---|---|---|
| Agent name | `DeepSeek V4.1 Flash Free` | Reported by the runtime to the agent; **not** independently verified |
| Provider ID | `opencode` | Same |
| Model ID | `deepseek-v4.1-flash-free` | Same |

This is an **environment-reported, self-described** identifier. It is not
recorded in any committed analysis artifact, cannot be checked by a reviewer
from the repository, and should not be treated as a confirmed fact about the
model that performed earlier phases. The `Free` suffix suggests a hosted
variant, but the exact build, quantization, serving configuration, and context
window are unknown. No claim is made that the same model or version performed
the 2026-11-05 verification phase, the main analysis, the external audits, or
this documentation.

**Recommended citation form:** "runtime-reported as `deepseek-v4.1-flash-free`
(provider `opencode`); unverified."

## 4. Tier 3 — unknown or unrecoverable information

The following are **not** recoverable from the repository:

- the model(s) used for the two separate AI computational audits in
  `results/analysis/human_verification/` (neither file names a model or
  author);
- whether the 2026-11-05 verification phase used the same model as the
  2026-11-12 main analysis or the 2026-11-18 corrections;
- all prompt texts and system instructions given to the agent;
- model-call timestamps (the run logs timestamp *script executions*, not
  model calls);
- sampling parameters (temperature, top-p, seed) for any AI call;
- any model used to draft or review documentation, including this file;
- the authorship of AI-assisted review comments beyond what the audit files
  state about their own independence from the analysis scripts.

## 5. Attribution of reviews and audits

The 2026-11-05 audit rounds are labeled "professor review" in
`mistakes.md`. Those labels record **human-directed review rounds** — project
oversight and accept/reject decisions by the project owner. The computational
authorship of the recomputations performed in those rounds is **not
documented**. This repository does **not** claim that the professor personally
performed, typed, or independently re-derived any calculation.

The two audit reports under `results/analysis/human_verification/` describe
themselves as calculated independently of the analysis scripts. They are
**separate AI computational audits**. Their model and author identities are
unrecorded. They are not a human audit, and they are not described as one.

Agent-written checks (VT-1…VT-10, the second calculation path in `src/07`,
and the duplicate-row instrument controls) are **agent-authored automated
verification**. Agreement between two agent-written paths rules out coding
slips; it does not establish independence.

No fully independent human audit has been completed. `VERIFICATION_PROTOCOL.md`
Stages 1–3 remain pending.

## 6. What can and cannot be concluded

| Question | Answer | Basis |
|---|---|---|
| Can the numerical analysis be reproduced? | **Yes**, given the raw data and the recorded environment | Deterministic scripts; bootstrap seed 42; SHA-256 anchor; `uv.lock` |
| Can the agent's behaviour be reproduced? | **No** | No prompts, model calls, or sampling parameters recorded |
| Can model-specific performance be claimed? | **No** | Model identity unverified; no controlled comparison |
| Was the analysis independently verified by a human? | **No** | `VERIFICATION_PROTOCOL.md` Stages 1–3 pending |

The absence of AI model logging does not undermine the arithmetic: the
statistical scripts, their inputs, and their outputs are preserved and
externally recomputed in part (see the coverage table in `README.md` §F). It
does undermine any claim that the *agent's reasoning process* is reproducible
or that a specific model version is responsible for the results.

## 7. Remediation for future runs

A future version should, at minimum:

1. log, for every AI call, the provider, exact model ID, prompt text (or a
   salted hash plus a stored copy), output, timestamp, and sampling
   parameters;
2. name the model and operator of every external audit;
3. add a verification check that fails when a model call is unlogged
   (operationalizing AGENTS.md rules 5 and 14);
4. keep the model log append-only and idempotent per script, as
   `results/analysis/model_log.md` now does for statistical models.

## 8. References

- `AGENTS.md` rules 5 and 14.
- `plan.md` §5 (model-call logging promise).
- `results/analysis/model_log.md` (statistical models only).
- `VERIFICATION_PROTOCOL.md` (pending human protocol).
- `mistakes.md` §R1 (irrecoverable 2026-11-05 failure logs) and §M6/§M8
  (errors found by the separate AI audits).
- `results/analysis/human_verification/independent_primary_audit.md` and
  `independent_robustness_audit.md`.
