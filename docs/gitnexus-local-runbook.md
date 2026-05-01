# GitNexus Local Runbook

## Purpose

This document records the local-only workaround that made GitNexus indexing succeed for this workspace on this Windows machine.

Use it when:
- GitNexus is reinstalled
- the machine changes
- indexing starts failing again after an upgrade

## Current Result

The workspace `D:\02-Projects\vibe` has been successfully indexed.

Verified status:
- `gitnexus status` shows `✅ up-to-date`
- `gitnexus list` includes this repository
- `gitnexus cypher "RETURN 1 AS c" --repo skill-runtime` exits with code `0`
- `gitnexus query "runtime service" --repo skill-runtime --limit 3` exits with code `0`
- `gitnexus context RuntimeService --repo skill-runtime` exits with code `0`

Latest verified index:
- Indexed: `2026-05-02 05:22:12`
- Indexed commit: `992f36e`
- Stats: `3032 files`, `8671 symbols`, `12478 edges`, `271 processes`

Current limitation:
- In the Codex session where the original crash happened, the GitNexus MCP transport may remain closed until Codex or the MCP server is restarted.
- The CLI path is usable after the local patches below.

## What Was Required

The successful path depended on five local adjustments inside the installed GitNexus package:

1. Fix Python fallback parsing to pass tree-sitter `bufferSize`
2. Allow `skipWorkers` to flow through the analyze pipeline
3. Temporarily skip VECTOR extension loading in LadybugDB on this Windows machine
4. Temporarily skip FTS/VECTOR extension loading in the LadybugDB read pool
5. Degrade GitNexus BM25 search to a slower `CONTAINS` graph scan on Windows when FTS is disabled

It also depended on running the index flow in single-thread mode.

## Local Patch Points

### 1. Python fallback parse buffer size

File:
- `D:\node-global\node_modules\gitnexus\dist\core\ingestion\languages\python\captures.js`

Required change:
- import `getTreeSitterBufferSize` from `../../constants.js`
- when the fallback parse runs, call:

```js
tree = getPythonParser().parse(sourceText, undefined, {
  bufferSize: getTreeSitterBufferSize(sourceText.length),
});
```

Reason:
- without this, long Python files can fail during the fallback parse path with scope extraction errors

### 2. Pass `skipWorkers` through analyze flow

File:
- `D:\node-global\node_modules\gitnexus\dist\core\run-analyze.js`

Required change:
- make `runPipelineFromRepo(repoPath, callback)` accept the third `options` argument
- pass that `options` object through so `skipWorkers: true` is honored

Reason:
- this allowed the pipeline to avoid the worker path and complete in single-thread mode

### 3. Skip VECTOR extension load

File:
- `D:\node-global\node_modules\gitnexus\dist\core\lbug\lbug-adapter.js`

Required change:
- temporarily skip automatic `loadVectorExtension()` during DB initialization

Reason:
- on this Windows machine, VECTOR-related initialization was associated with database write failures during indexing

### 4. Skip FTS/VECTOR extension load in the read pool

File:
- `D:\node-global\node_modules\gitnexus\dist\core\lbug\pool-adapter.js`

Required change:
- in the pool initialization paths, avoid calling FTS/VECTOR extension loading for the pooled read connections
- keep `shared.ftsLoaded = false` and `shared.vectorLoaded = false`

Reason:
- on this Windows machine, `LOAD EXTENSION fts` crashes the native `@ladybugdb/core` process during pooled query startup
- when this happens through MCP, Codex sees only `Transport closed`, which makes GitNexus look like it is not configured

### 5. Use a Windows-safe BM25 fallback

File:
- `D:\node-global\node_modules\gitnexus\dist\core\search\bm25-index.js`

Required change:
- when `process.platform === 'win32'` or `GITNEXUS_DISABLE_LBUG_FTS=1`, skip FTS index creation/querying
- use a slower `MATCH ... WHERE lower(...) CONTAINS ...` fallback against `File`, `Function`, `Class`, `Method`, and `Interface`

Reason:
- disabling FTS in the pool prevents crashes, but query search still needs a non-FTS path
- the fallback is lower quality than real FTS/vector ranking, but it keeps `gitnexus query` and MCP search alive instead of killing the transport

## Recommended Recovery Steps

If GitNexus is reinstalled or upgraded and indexing breaks again, use this order:

1. Confirm GitNexus is installed and callable

```powershell
gitnexus --version
gitnexus mcp --help
```

2. Re-apply the five local patch points above

3. Re-run indexing for this workspace in single-thread mode

Use a local Node script or equivalent call path that triggers:

```js
runFullAnalysis("D:/02-Projects/vibe", {
  force: true,
  skipAgentsMd: true,
  skipWorkers: true,
  embeddings: false,
});
```

4. Verify registration

```powershell
gitnexus status
gitnexus list
gitnexus cypher "RETURN 1 AS c" --repo skill-runtime
gitnexus query "runtime service" --repo skill-runtime --limit 3
gitnexus context RuntimeService --repo skill-runtime
```

## Expected Healthy State

When recovery succeeds, expect:
- the repository appears in `gitnexus list`
- `gitnexus status` shows `✅ up-to-date`
- the indexed and current commits match
- `cypher`, `query`, and `context` exit with code `0`
- dashboard-related files are visible through structural queries, for example:

```powershell
gitnexus cypher "MATCH (f:File) WHERE lower(f.filePath) CONTAINS 'dashboard' RETURN f.filePath LIMIT 20" --repo skill-runtime
```

## Important Notes

- This is a local workaround, not proof that the default upstream path is fully fixed.
- If GitNexus is upgraded, these local patches may be overwritten.
- Do not assume another machine will need the exact same workaround.
- Because FTS/VECTOR are disabled locally, keyword and semantic ranking quality is degraded. Use `cypher` or `context` for more reliable structural lookup.
