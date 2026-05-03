# Runtime Read-Only Panel Plan

## Goal

Turn the static dashboard into a read-only interactive panel. The first useful loop is:

1. scan the central workflow skill cards
2. click one skill
3. inspect its full metadata in a side drawer
4. close the drawer without changing runtime state

This is not an operations console yet. It must not promote, reject, edit, archive, install, or write global skill files.

## First Interaction

The first implementation target is the central skill library.

- Each visible workflow skill card is clickable.
- Clicking opens a right-side detail drawer.
- The drawer shows only already-rendered dashboard data:
  - display name
  - raw skill name
  - status
  - summary
  - usage count
  - source trajectory count
  - group/source label
  - import provenance when present
- Closing the drawer returns the user to the same view.

## UI Boundary

- Keep the existing app shell, sidebar, page headers, and card grid.
- Use one drawer component shared by future read-only details.
- The drawer must work without a backend server because the dashboard is still static HTML.
- All detail data should be embedded as escaped `data-*` attributes on the clicked card.
- No buttons should imply mutation. Use labels such as `只读详情`, `关闭`, and `来源信息`.

## Validation

The first stage is complete when:

- rendered HTML contains the drawer contract
- skill cards expose the fields needed by the drawer
- JavaScript opens and closes the drawer without view navigation
- generated dashboard screenshots show the drawer in desktop and mobile-safe layouts
- targeted dashboard tests, Python syntax checks, and `git diff --check` pass

## Stop Condition

Do not add promote/reject/edit/archive actions in this stage. If the next request requires writing runtime state, run a separate direction review for an operations panel.
