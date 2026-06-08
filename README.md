# Cognis Neural Suite

> **102+ single-purpose, self-hostable, MCP-native tools** for security, AI, compliance, data, dev, and business — by [Cognis Digital](https://cognis.digital).

[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE) ![Tools](https://img.shields.io/badge/tools-102%2B-6b46c1)

## What this is

Each tool is its own repo (CLI + MCP server + devcontainer + tests + demos). They share `cognis-core` primitives so findings compose, and every one runs locally and self-hosted.

## Install any tool

```bash
pip install cognis-<tool>
```

## The catalog


### 🛡️ AI Security & Governance (11)

| Tool | Description |
|---|---|
| [adversa](https://github.com/cognis-digital/adversa) | LLM red-team harness — OWASP LLM Top 10 + MITRE ATLAS attack packs |
| [aegis](https://github.com/cognis-digital/aegis) | AI Agent Permission & Access Auditor — surfaces the lethal trifecta of credentials + injection + reach |
| [agentlog](https://github.com/cognis-digital/agentlog) | Agentic workflow replay & audit with OTel GenAI semantic conventions |
| [aicard](https://github.com/cognis-digital/aicard) | Auto-generated NIST AI RMF / EU AI Act Annex IV model & system cards |
| [biascope](https://github.com/cognis-digital/biascope) | Embedded bias probe suite — demographic / occupational / geographic |
| [guardpost](https://github.com/cognis-digital/guardpost) | Runtime agent firewall — PII redaction, rate limits, policy enforcement |
| [hallumark](https://github.com/cognis-digital/hallumark) | LLM hallucination & grounding auditor for RAG systems |
| [ledgermind](https://github.com/cognis-digital/ledgermind) | Local LLM cost & token forensics proxy with anomaly detection |
| [mcpharden](https://github.com/cognis-digital/mcpharden) | MCP server hardening linter — capability declarations, transport, tool descriptions |
| [promptmirror](https://github.com/cognis-digital/promptmirror) | Prompt-injection & indirect-injection scanner for any LLM context input |
| [ragshield](https://github.com/cognis-digital/ragshield) | RAG corpus poisoning detector — embedding anomalies, backdoor triggers |

### 🤖 AI Agents & LLMOps (8)

| Tool | Description |
|---|---|
| [agentsmith](https://github.com/cognis-digital/agentsmith) | Config-first scaffolding and orchestration for multi-agent workflows |
| [evalbench](https://github.com/cognis-digital/evalbench) | Offline LLM / agent eval harness with regression gates |
| [memorybank](https://github.com/cognis-digital/memorybank) | Portable long-term memory store for agents, exposed over MCP |
| [modelroute](https://github.com/cognis-digital/modelroute) | Local model router / proxy across Ollama, vLLM, and cloud with fallback |
| [promptpack](https://github.com/cognis-digital/promptpack) | Versioned prompt / template registry with A/B and rollbacks |
| [ragkit](https://github.com/cognis-digital/ragkit) | Batteries-included local RAG pipeline — ingest, index, serve |
| [skillhub](https://github.com/cognis-digital/skillhub) | Local skill registry and installer for AI agents |
| [toolguard](https://github.com/cognis-digital/toolguard) | Runtime allowlist and policy for agent tool-calls |

### 🔵 Blue Team (6)

| Tool | Description |
|---|---|
| [canarynet](https://github.com/cognis-digital/canarynet) | Self-hosted canary token network — AWS keys, DNS, docs, web URLs |
| [edrgap](https://github.com/cognis-digital/edrgap) | EDR coverage & bypass detector — reconciles MDM + EDR + AD inventories |
| [honeytrace](https://github.com/cognis-digital/honeytrace) | Active-decoy network lure system — SSH, RDP, SMB, web honeypots |
| [phishforge](https://github.com/cognis-digital/phishforge) | Open-source phishing simulation — campaigns, templates, training |
| [sbomgate](https://github.com/cognis-digital/sbomgate) | Continuous SBOM diff & vulnerability watch with maintainer-change tracking |
| [sentrylog](https://github.com/cognis-digital/sentrylog) | Single-file SIEM for small teams — Sigma rules + multi-source ingest |

### ⚔️ Red Team (5)

| Tool | Description |
|---|---|
| [c2detect](https://github.com/cognis-digital/c2detect) | C2 server fingerprinter — Cobalt Strike, Sliver, Mythic, Havoc, Brute Ratel |
| [crackq](https://github.com/cognis-digital/crackq) | Self-hosted password cracking queue — multi-user hashcat with audit log |
| [payloadlab](https://github.com/cognis-digital/payloadlab) | Static malicious payload analyzer — PE/ELF/LNK/macro/OneNote |
| [pwnreview](https://github.com/cognis-digital/pwnreview) | Pentest report generator — YAML findings to CREST-grade PDF |
| [redpath](https://github.com/cognis-digital/redpath) | Active Directory attack path mapper — minimum-cost paths + remediation priority |

### 🔍 OSINT (6)

| Tool | Description |
|---|---|
| [corpmap](https://github.com/cognis-digital/corpmap) | Corporate structure & beneficial-ownership mapper |
| [cryptotrace](https://github.com/cognis-digital/cryptotrace) | Free-tier blockchain investigator — ETH/BTC clustering + sanctions xref |
| [darkmirror](https://github.com/cognis-digital/darkmirror) | Surface-web mirror of public Tor leak-site index for brand monitoring |
| [geolens](https://github.com/cognis-digital/geolens) | Image geolocation toolkit — EXIF, sun-shadow, OCR, reverse-search |
| [maritimeint](https://github.com/cognis-digital/maritimeint) | AIS vessel tracking & sanctions-evasion anomaly detection |
| [personagraph](https://github.com/cognis-digital/personagraph) | Identity resolution dossier — username/email/phone cross-platform |

### 🏛️ Federal & Compliance (6)

| Tool | Description |
|---|---|
| [checkpoint-ai](https://github.com/cognis-digital/checkpoint-ai) | NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator |
| [clearancepath](https://github.com/cognis-digital/clearancepath) | Personnel clearance hygiene tracker — SF-86, SEAD-3/4, training currency |
| [cmmcmap](https://github.com/cognis-digital/cmmcmap) | CMMC Level 2 practice mapper — stack-aware SSP skeleton generator |
| [fedramplens](https://github.com/cognis-digital/fedramplens) | FedRAMP boundary visualizer & OSCAL-format SSP/POAM generator |
| [gsafinder](https://github.com/cognis-digital/gsafinder) | GSA Schedule opportunity surveyor — SAM.gov + eBuy + FedConnect |
| [sbirscout](https://github.com/cognis-digital/sbirscout) | SBIR/STTR topic discovery — DSIP + SBIR.gov + NIH digest with bid scoring |

### 🕵️ Privacy (7)

| Tool | Description |
|---|---|
| [breachwatch](https://github.com/cognis-digital/breachwatch) | Personal breach aggregator — HIBP + DeHashed + stealer-log triage |
| [optout](https://github.com/cognis-digital/optout) | Automated data-broker opt-out engine — top 50 brokers, CCPA/GDPR letters |
| [piicomb](https://github.com/cognis-digital/piicomb) | Local PII discovery in your own files — SSN/CC/passport/DL/email/phone/DOB |
| [privacyshell](https://github.com/cognis-digital/privacyshell) | Hardened browser profile generator — Firefox / LibreWolf / Brave |
| [recall](https://github.com/cognis-digital/recall) | Privacy-first local RAG over personal data — encrypted, audit-logged |
| [trackblock](https://github.com/cognis-digital/trackblock) | Family phone stalkerware audit — MVT-class iOS/Android forensics |
| [vaultmap](https://github.com/cognis-digital/vaultmap) | Personal asset & account inventory — estate-planning-grade encrypted |

### 📡 Network (3)

| Tool | Description |
|---|---|
| [certpatrol](https://github.com/cognis-digital/certpatrol) | TLS cert lifecycle & rogue-issuance watch via Certificate Transparency |
| [dnsaudit](https://github.com/cognis-digital/dnsaudit) | DNS posture & misconfiguration scanner — SPF/DKIM/DMARC/DNSSEC/CAA |
| [egresswatch](https://github.com/cognis-digital/egresswatch) | Server-side outbound connection auditor — eBPF/Falco wrapper |

### 📰 Information Integrity (4)

| Tool | Description |
|---|---|
| [claimtrace](https://github.com/cognis-digital/claimtrace) | Misinformation provenance tracer — earliest-known appearance graph |
| [deepcheck](https://github.com/cognis-digital/deepcheck) | Lightweight synthetic-media detector with C2PA validation |
| [electionlens](https://github.com/cognis-digital/electionlens) | Influence-operations pattern monitor for election periods |
| [narrativediff](https://github.com/cognis-digital/narrativediff) | News bias & framing diff across 50+ outlets per event |

### 🔗 Supply Chain (4)

| Tool | Description |
|---|---|
| [depgraph](https://github.com/cognis-digital/depgraph) | Dependency risk visualizer — Scorecard + OSV + typosquat + maintainer signals |
| [ossaudit](https://github.com/cognis-digital/ossaudit) | OSS license compliance auditor — AGPL contamination + NOTICE generation |
| [pipewatch-pro](https://github.com/cognis-digital/pipewatch-pro) | CI/CD supply-chain auditor — GH Actions / GitLab CI / OWASP CI/CD Top 10 |
| [secretsweep](https://github.com/cognis-digital/secretsweep) | Repo secret scanner + auto-rotator across providers |

### 🧰 Developer Tools (10)

| Tool | Description |
|---|---|
| [apidiff](https://github.com/cognis-digital/apidiff) | Breaking-change detector for OpenAPI / GraphQL across commits |
| [codeglance](https://github.com/cognis-digital/codeglance) | Repo onboarding map — architecture + hotspots for humans and agents |
| [envdoctor](https://github.com/cognis-digital/envdoctor) | .env validator, secret-presence and config-drift checker |
| [flakefinder](https://github.com/cognis-digital/flakefinder) | Flaky-test detector from CI history with quarantine suggestions |
| [gitstory](https://github.com/cognis-digital/gitstory) | Changelog and release notes from conventional commits |
| [licenselens](https://github.com/cognis-digital/licenselens) | Dependency license + SBOM gate, developer-CLI first |
| [mcpforge](https://github.com/cognis-digital/mcpforge) | Scaffold, test, and publish MCP servers in minutes |
| [promptlint](https://github.com/cognis-digital/promptlint) | Lint, version, and test prompts as code with a CI gate |
| [shipcheck](https://github.com/cognis-digital/shipcheck) | Dockerfile linter with image-size and CVE advisories |
| [tokenmeter](https://github.com/cognis-digital/tokenmeter) | Token and cost counter / budgeter for LLM apps, CI-ready |

### 🗄️ Data & Datasets (8)

| Tool | Description |
|---|---|
| [csvlens](https://github.com/cognis-digital/csvlens) | Fast CLI for profiling and cleaning huge CSV / Parquet files |
| [datasetcard](https://github.com/cognis-digital/datasetcard) | Auto Dataset Cards / datasheets with Croissant + provenance |
| [duckprobe](https://github.com/cognis-digital/duckprobe) | Zero-setup data-quality checks on any file or warehouse via DuckDB |
| [embedaudit](https://github.com/cognis-digital/embedaudit) | Embedding / vector-store drift and poisoning audit |
| [lineagemap](https://github.com/cognis-digital/lineagemap) | Column-level lineage extracted from SQL and dbt |
| [piiscan](https://github.com/cognis-digital/piiscan) | PII discovery across warehouses and lakes (data-side scanner) |
| [schemadrift](https://github.com/cognis-digital/schemadrift) | Schema-change detector and data-contract tests |
| [seedforge](https://github.com/cognis-digital/seedforge) | Synthetic test-data generator with referential integrity |

### 📋 Compliance & GRC (8)

| Tool | Description |
|---|---|
| [accessreview](https://github.com/cognis-digital/accessreview) | Periodic user-access-review (UAR) campaign runner |
| [auditrail](https://github.com/cognis-digital/auditrail) | Tamper-evident audit-log aggregator with hash-chained attestation |
| [dpiaforge](https://github.com/cognis-digital/dpiaforge) | DPIA and EU AI Act impact-assessment generator |
| [frameworkmap](https://github.com/cognis-digital/frameworkmap) | Crosswalk controls across NIST, ISO 27001, SOC 2, CMMC, PCI |
| [gdprkit](https://github.com/cognis-digital/gdprkit) | GDPR/CCPA DSAR, RoPA, and cookie-consent toolkit |
| [policyforge](https://github.com/cognis-digital/policyforge) | Auto-generate security policies from a short questionnaire |
| [soc2box](https://github.com/cognis-digital/soc2box) | SOC 2 evidence collector and control tracker, self-hosted |
| [vendorvet](https://github.com/cognis-digital/vendorvet) | Third-party / vendor risk questionnaires with SBOM cross-ref |

### 💼 Business Ops (10)

| Tool | Description |
|---|---|
| [boardroom](https://github.com/cognis-digital/boardroom) | Investor-update and KPI one-pager generator from your metrics |
| [churnlens](https://github.com/cognis-digital/churnlens) | Self-hosted SaaS metrics — MRR, churn, LTV from Stripe or CSV |
| [invoctl](https://github.com/cognis-digital/invoctl) | CLI invoicing + payment-link generator with PDF and a local ledger |
| [leadforge](https://github.com/cognis-digital/leadforge) | Lightweight MCP-native CRM pipeline with email sequences |
| [meetingcost](https://github.com/cognis-digital/meetingcost) | Compute the dollar cost of meetings from your calendar (.ics) |
| [orgchart](https://github.com/cognis-digital/orgchart) | Org charts and headcount plans generated from CSV / HRIS export |
| [paywatch](https://github.com/cognis-digital/paywatch) | Recurring-charge and subscription detector from bank/Plaid CSV |
| [quotecraft](https://github.com/cognis-digital/quotecraft) | Proposal / quote / SOW generator — YAML to branded PDF |
| [runbookgen](https://github.com/cognis-digital/runbookgen) | Incident runbook and SOP generator from templates |
| [seataudit](https://github.com/cognis-digital/seataudit) | SaaS license, seat-usage and shadow-IT auditor |

### 📈 DevOps & Observability (6)

| Tool | Description |
|---|---|
| [alertmux](https://github.com/cognis-digital/alertmux) | Alert dedup, correlation, and routing in front of Grafana / PagerDuty |
| [cloudbill](https://github.com/cognis-digital/cloudbill) | Multi-cloud cost report, anomaly detection, and FOCUS export |
| [k8scost](https://github.com/cognis-digital/k8scost) | Kubernetes cost and rightsizing advisor with no Prometheus dependency |
| [otelbox](https://github.com/cognis-digital/otelbox) | One-command OpenTelemetry collector + dashboards bundle |
| [probesite](https://github.com/cognis-digital/probesite) | Synthetic uptime and Playwright checks exported to Prometheus |
| [statuskit](https://github.com/cognis-digital/statuskit) | Self-hosted status page with incident timeline and subscribers |

## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — see [LICENSE](LICENSE).

