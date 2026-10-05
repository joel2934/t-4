# Fixes applied

## 1. Duplicate `"metrics"` key in `CONCEPT_HINTS` (app/main.py)

`CONCEPT_HINTS` is a single dict literal, so a repeated key silently overwrites the
first one. `"metrics"` was defined twice:

- once for the fraud-classifier question's rubric concept (precision/recall/F1/PR-AUC)
- once for the forecasting question's rubric concept (MAE/WAPE)

Python kept only the second definition, so the local (no-API-key) rubric scorer could
never detect precision/recall/F1/PR-AUC language when grading the fraud-classifier
question — even fully correct answers were marked "missing: metrics" and scored low.

**Fix:** renamed the forecasting question's concept to `forecast_metrics` in both
`app/main.py` (`CONCEPT_HINTS`) and `app/questions.py` (that question's `rubric` dict),
so the two concepts no longer collide.

**Also added** missing `CONCEPT_HINTS` entries for `hypotheses` and `statistics`
(used by the "dashboard conversion rate dropped" rubric), which previously fell back
to literal substring-matching the raw concept name.

**Verified impact** via `GET /api/evaluation/validate` (the app's own expert-labelled
benchmark):

| | Before | After |
|---|---|---|
| Mean absolute error | 18.3 | 9.7 |
| Agreement within 15 pts | 50% | 83% |
| Model-evaluation question errors | 27, 30 | 1, 4 |

## 2. Outer stage sequencing moved into an explicit LangGraph `StateGraph`

Previously, stage sequencing (warmup → technical → case → behavioral → complete) was
plain Python index arithmetic over a `STAGE_PLAN` list, duplicated in two places
(`advance_stage_node` and a dead, never-called `InterviewGraph.advance()` method).
Only the score/memory/difficulty adaptation ran through LangGraph.

**Fix:** added a `stage_graph` (`StateGraph[StageState]`) with one node per named
interview stage (`warmup`, `technical`, `case`, `behavioral`) plus an `advance` node.
`START` conditionally routes to whichever stage the learner is currently in; each
stage node's outgoing conditional edge checks its question quota and either stays
(`END`) or routes through `advance` to the next staged node. `advance_stage_node` in
the existing scoring-transition graph now simply invokes `stage_graph` instead of
duplicating the sequencing logic. The dead `InterviewGraph.advance()` method was
removed.

This makes the explicit "warmup → technical → case study → behavioral → report"
sequence from the problem statement a literal LangGraph structure, not just an
implicit list, while keeping the exact same runtime behavior (verified with a full
end-to-end interview run through all four stages to completion).

## Note on existing local data

If you have a previously-seeded `interview_prep.db` or `chroma_store/` from before
this fix, delete them before running — the question bank is only seeded once
(`seed()` no-ops if questions already exist), so a stale DB would keep the old
`"metrics"` rubric key for the forecasting question.
