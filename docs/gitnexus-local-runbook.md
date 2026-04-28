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

## What Was Required

The successful path depended on three local adjustments inside the installed GitNexus package:

1. Fix Python fallback parsing to pass tree-sitter `bufferSize`
2. Allow `skipWorkers` to flow through the analyze pipeline
3. Temporarily skip VECTOR extension loading in LadybugDB on this Windows machine

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

## Recommended Recovery Steps

If GitNexus is reinstalled or upgraded and indexing breaks again, use this order:

1. Confirm GitNexus is installed and callable

```powershell
gitnexus --version
gitnexus mcp --help
```

2. Re-apply the three local patch points above

3. Re-run indexing for this workspace in single-thread mode

Use a local Node script or equivalent call path that triggers:

```js
runFullAnalysis("D:/02-Projects/vibe", {
  force: true,
  skipAgentsMd: true,
  skipWorkers: true,
});
```

4. Verify registration

```powershell
gitnexus status
gitnexus list
```

## Expected Healthy State

When recovery succeeds, expect:
- the repository appears in `gitnexus list`
- `gitnexus status` shows `✅ up-to-date`
- the indexed and current commits match

## Important Notes

- This is a local workaround, not proof that the default upstream path is fully fixed.
- If GitNexus is upgraded, these local patches may be overwritten.
- Do not assume another machine will need the exact same workaround.
