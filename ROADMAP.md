# Roadmap

Direction for the Cognis Neural Suite catalog and its shared `livesearch`
live-data module. This is a living document — proposals and RFCs welcome via
Discussions/Issues.

## Principles

- **Additive & backward-compatible.** Existing functions, CLI flags, and the uniform
  item shape stay stable. New capability arrives as new flags/functions.
- **Keyless & dependency-free at runtime.** No API keys; standard library only. Dev
  tooling (pytest/ruff) stays in the `dev` extra.
- **Tested before shipped.** Every new backend/format lands with offline tests and CI.

## Near-term (next release)

- **More output sinks.** SARIF and Atom re-emit so `livesearch` output can feed the
  suite's security tools and be re-published as a feed.
- **Time-window helpers.** `--since` / `--until` absolute-date bounds alongside the
  relative `--when` / `--since-days`.
- **Source health report.** `--harvest --report` to print per-source item counts and
  flag dead/empty feeds without failing the run.
- **Config file.** Optional `livesearch.toml` for default `when`, `limit`, and a named
  set of harvest sources.

## Mid-term

- **Pluggable backends.** A small registry so additional keyless search/feed backends
  can be registered without touching the core module.
- **Caching layer.** Opt-in on-disk cache with TTL to avoid re-fetching identical
  queries within a short window (useful in CI and batch harvests).
- **Concurrency.** Bounded parallel fetching in `harvest` for large source lists, with
  the same deterministic de-dupe/sort output.
- **Enrichment hooks.** Optional per-item callbacks (language detection, keyword
  tagging) that stay off by default and dependency-free.

## Long-term

- **Streaming mode.** Long-running `--watch` that polls sources on an interval and
  emits new items as NDJSON for agent pipelines.
- **MCP server.** Expose `web_search` / `fetch_feed` / `harvest` as MCP tools so agents
  can drive live search directly, consistent with the rest of the suite.
- **Cross-port parity.** Bring the JS/Go/Rust ports in `ports/` to feature parity with
  the Python reference (same item shape, same output formats).

## Non-goals

- Requiring API keys or paid data providers.
- Adding heavyweight runtime dependencies to the core module.
- Removing or breaking existing public functions, flags, or the item schema.
