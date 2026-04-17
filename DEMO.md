# Demo

This demo validates the minimum self-evolving skill runtime loop:

1. Record a trajectory
2. Distill it into a staging skill
3. Audit the skill
4. Promote it to the active store
5. Search the skill index
6. Execute the promoted skill

## Directory Setup

```text
demo/
  input/
    a.txt
    b.txt
  output/

trajectories/
  demo_merge_text_files.json

skill_store/
  staging/
  active/
  archive/
  rejected/
  index.json

audits/
```

## Example Inputs

`demo/input/a.txt`

```text
hello from file a
```

`demo/input/b.txt`

```text
hello from file b
```

## Validation Commands

### 1. Register the trajectory

```bash
python scripts/skill_cli.py log-trajectory --file trajectories/demo_merge_text_files.json
```

### 2. Distill a staging skill

```bash
python scripts/skill_cli.py distill --trajectory trajectories/demo_merge_text_files.json --skill-name merge_text_files_generated
```

### 3. Audit the staging skill

```bash
python scripts/skill_cli.py audit --file skill_store/staging/merge_text_files_generated.py
```

### 4. Promote the skill

```bash
python scripts/skill_cli.py promote --file skill_store/staging/merge_text_files_generated.py
```

Only a `passed` audit result should allow promotion.

### 5. Search the active index

```bash
python scripts/skill_cli.py search --query "merge txt files into markdown"
```

### 6. Execute the promoted skill

```bash
python scripts/skill_cli.py execute --skill merge_text_files_generated --args-file demo/execute_args.json
```

## What This Demo Proves

- trajectories can be validated and stored
- a staging skill can be generated
- static audit reports are written to disk
- promotion is blocked unless audit status is `passed`
- promoted skills are indexed and searchable
- active skills can be loaded and executed
