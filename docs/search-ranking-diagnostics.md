# Search Ranking Diagnostics

Date: 2026-05-05

Scope:
this document analyzes the current fixed local search baseline only.
It does not add queries, change retrieval behavior, or reinterpret the baseline as product-policy evidence.

## Per-Query Top Result Summary

### `exact_merge_english`

- Query: `merge txt files into markdown`
- Top result: `merge_text_files`
- Score: `1.67`
- Recommended skill: `merge_text_files`
- Main factors:
  - strong lexical overlap on `merge`, `txt`, `files`, `markdown`
  - summary boost
  - small alias boost
  - tags, provenance, usage, audit

Top false neighbor:

- `directory_text_cleanup_dogfood` at `0.825`
- Why it appears:
  - overlaps on broad file/text tokens such as `files` and `txt`
  - gets summary, tags, provenance, and audit boosts

Observation:

- The top-1 margin is still wide enough that recommendation behavior is stable.

### `fuzzy_merge_english`

- Query: `combine text files into one markdown document`
- Top result: `merge_text_files`
- Score: `1.67`
- Recommended skill: `merge_text_files`
- Main factors:
  - strong lexical overlap
  - stronger alias contribution than the exact merge query
  - summary, tags, provenance, usage, audit

Top false neighbors:

- `directory_text_cleanup_dogfood` at `0.6667`
- `json_to_csv_dogfood` at `0.3833`

Why they appear:

- `directory_text_cleanup_dogfood` carries broad text/file metadata and looks partially relevant to generic text-file work
- `json_to_csv_dogfood` is pulled in mainly by the generic token `text` through provenance/audit-supported lexical overlap

Observation:

- This is the clearest current false-neighbor pattern:
  broad text/file metadata causes weak utility neighbors for fuzzy merge intent.

### `structured_json_to_csv`

- Query: `convert json records to csv`
- Top result: `json_to_csv_dogfood`
- Score: `1.55`
- Recommended skill: `json_to_csv_dogfood`

False neighbors:

- none in the current top results

Observation:

- The JSON-to-CSV metadata is narrow and clean enough that the result set collapses to one obvious answer.

### `maintainer_handoff_workflow`

- Query: `resume handoff update tasks decisions`
- Top result: `session_handoff_maintenance`
- Score: `1.14`
- Recommended skill: `session_handoff_maintenance`

False neighbors:

- none in the current top results

Observation:

- The maintainer workflow metadata is specific enough that the fixed fixture subset does not produce competing workflow noise.

### `chinese_merge_query`

- Query: `把多个文本文件合并成一个文档`
- Top result: `merge_text_files`
- Score: `1.52`
- Recommended skill: `merge_text_files`
- Main factors:
  - explicit alias match
  - usage boost
  - audit boost

False neighbors:

- none in the current top results

Observation:

- The query works because `merge_text_files` declares explicit `search_aliases`.
- This is not general Chinese retrieval.
- There is also one diagnostic caveat:
  current scoring reports `lexical=1.0` for this query because alias-matched terms are folded into `matched_terms`, even though ordinary ASCII tokenization contributes no Chinese tokens.
  That makes the current score breakdown explainable enough for local debugging, but not a pure tokenization trace.

### `negative_email_newsletter`

- Query: `send an email newsletter campaign`
- Top result: none
- Recommended skill: none

Observation:

- No false recommendation and no low-score visible noise in the current fixture subset.

### `negative_chinese_email_campaign`

- Query: `发送邮件营销活动`
- Top result: none
- Recommended skill: none

Observation:

- No false recommendation and no visible alias bleed-through from the Chinese merge alias.

## False-Neighbor Observations

Current false neighbors are concentrated in the merge queries:

- `directory_text_cleanup_dogfood` is the main false neighbor for both merge queries
- `json_to_csv_dogfood` is a weaker false neighbor for the fuzzy merge query

The pattern is not random.
It comes from broad metadata:

- generic tokens like `text`, `files`, `directory`, `folder`
- broad summaries describing text-file manipulation without enough task-shape boundaries
- permissive tags that help recall but also create neighbor noise

Within the fixed fixture subset, the workflow query and structured conversion query are much cleaner.

## Negative-Query Noise Observations

Current negative-query noise is low:

- English negative query returns no recommended skill and no top results
- Chinese negative query returns no recommended skill and no top results

For the current fixture subset, this means there is no immediate evidence that recommendation thresholds are too weak.

The caveat is scope:

- this is a small fixed fixture set
- absence of noise here does not prove broad negative-query robustness across the full active library

## Alias Boost Observations

Alias boost is visible but not obviously too strong in the current baseline:

- exact merge English query: alias contribution is small
- fuzzy merge English query: alias contribution helps stabilize the intended merge result
- Chinese merge query: alias support is the reason the query works at all

Current judgment:

- alias boost is not obviously overpowered in this fixed baseline
- there is no evidence that it is causing negative-query pollution
- the current Chinese success should be understood as explicit metadata recall, not language understanding

## Metadata Quality Issues Found

Main issues:

- `directory_text_cleanup_dogfood` has broad utility wording and tags that make it a neighbor for merge-style text-file queries
- `json_to_csv_dogfood` still carries enough generic `text` framing to show up weakly for fuzzy merge text queries
- `merge_text_files` benefits from a very high usage boost (`0.12` cap reached), which helps stability but also means score margins are not purely about query-text fit
- current diagnostic wording can make alias-driven Chinese success look more lexical than it really is

There is also a broader repository note:

- many active metadata files outside the fixed fixture subset are thin workflow adapters with broad words like `workflow`, `report`, `output_path`, and `next_action`
- they are not currently part of this baseline fixture import set
- if the fixture set broadens later, metadata hygiene will matter more before weight tuning

## Is Any Ranking-Weight Change Justified?

Current answer: not yet.

Reason:

- all 7 baseline queries still match cleanly
- there is no current negative-query recommendation noise
- the strongest false neighbors are explainable by broad metadata, not a clearly broken weighting regime
- the top-1 margins are still strong enough that recommendation behavior is stable

If weights move now, it would be hard to prove that the change solves a real ranking problem rather than masking metadata breadth.

## What Should Not Change Yet

- do not add new queries in this slice
- do not change retrieval algorithm structure
- do not tune ranking weights yet
- do not introduce embedding, external retrieval, or LLM retrieval
- do not use these ranking results as evidence for widening `default-in`

## Next-Step Judgment

The next move should be metadata quality tightening before ranking-weight adjustment.

Most likely targets:

- narrow broad tags on text/file utility skills where they create weak neighbor noise
- tighten summaries so adjacent file-processing skills describe their specific task shape more clearly
- keep alias metadata explicit and minimal

Only after that kind of metadata cleanup would a small ranking-weight adjustment be justified.

## Why This Is Not Default-In Evidence

- Ranking diagnostics measure local retrieval quality, not runtime-entry safety
- Clean top-1 ranking on a small fixed baseline does not answer whether tasks should enter the runtime lane automatically
- Alias-driven Chinese recall does not imply broader workflow safety or policy confidence

There is still no evidence here that supports widening `default-in`.
