# OneUptime vs Uptime Kuma vs Grafana

**Scope:** Self-hosted Docker Compose deployment. FastAPI backend health monitoring, SSL certificate monitoring for `demo.ohc.network`, incident management with user assignment, and Jira Service Management (JSM) / Slack / GitHub Issues integration.
**Source:** Official documentation and source code. Verified May 2026.
**Grafana version:** v13.0 ([released April 2026](https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v13-0/), [GrafanaCON 2026](https://grafana.com/blog/grafanacon-2026-announcements/)).

## Table of Contents

1. [Summary](#summary)
2. [Quick Reference](#quick-reference)
3. [Monitoring Capabilities](#monitoring-capabilities)
4. [Notifications and Integrations](#notifications-and-integrations)
5. [Incident Management and Alert Routing](#incident-management-and-alert-routing)
6. [Jira, Slack, and GitHub Issues](#jira-slack-and-github-issues)
7. [Infrastructure Requirements](#infrastructure-requirements)
8. [Pricing](#pricing)
9. [Recommendation](#recommendation)

## Summary

**[Uptime Kuma](https://github.com/louislam/uptime-kuma)** is a single-purpose uptime monitor. One container, SQLite database, [90+ native notification providers](https://github.com/louislam/uptime-kuma/tree/master/src/components/notifications) plus [78+ more via Apprise](https://github.com/louislam/uptime-kuma/wiki/Notification-Methods). No incident management, no on-call scheduling, no user assignment. ~87k GitHub stars, ~156M Docker pulls (docker.io + ghcr.io, [April 2026](https://github.com/louislam/uptime-kuma/wiki)), MIT licensed.

**[OneUptime](https://github.com/OneUptime/oneuptime)** is a full operations platform covering monitoring, incident lifecycle, on-call duty, status pages, logs, APM, traces, and workflow automation. Requires PostgreSQL, ClickHouse, and Redis. [Apache 2.0 licensed](https://github.com/OneUptime/oneuptime/blob/master/LICENSE), self-hosted.

**[Grafana](https://github.com/grafana/grafana)** is a visualization and alerting platform. [Grafana OSS v13](https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v13-0/) is free and self-hosted, covering dashboards, metrics, logs (Loki), traces (Tempo), and alerting (built-in Alertmanager). HTTP/SSL synthetic monitoring requires an external exporter ([Blackbox Exporter](https://github.com/prometheus/blackbox_exporter)) or [Grafana Cloud Synthetic Monitoring](https://grafana.com/docs/grafana-cloud/testing/synthetic-monitoring/). Incident management and on-call scheduling are only available in [Grafana Cloud IRM](https://grafana.com/products/cloud/irm/) - the self-hosted OnCall OSS project was [archived on March 24, 2026](https://grafana.com/docs/oncall/latest/set-up/open-source/).

## Quick Reference

| Feature                              | Uptime Kuma                  | OneUptime                            | Grafana                                            |
| ------------------------------------ | ---------------------------- | ------------------------------------ | -------------------------------------------------- |
| Primary purpose                      | Uptime monitoring + alerts   | Full ops lifecycle                   | Visualization, alerting, observability             |
| Self-hosted option                   | Yes - single container       | Yes - 7 containers                   | Yes (OSS v13) - but IRM is cloud-only              |
| License                              | MIT                          | [Apache 2.0](https://github.com/OneUptime/oneuptime/blob/master/LICENSE) | AGPLv3 (OSS), proprietary (Enterprise/Cloud) |
| HTTP / SSL monitoring                | Yes - built-in               | Yes - built-in                       | Needs Blackbox Exporter or Grafana Cloud Synthetics |
| Incident management                  | No                           | Yes - full lifecycle, self-hosted    | Cloud IRM only ($20/user/month after 3 free)       |
| On-call scheduling                   | No                           | Yes - self-hosted                    | [Cloud IRM](https://grafana.com/products/cloud/irm/) only. [OnCall OSS archived March 2026](https://grafana.com/docs/oncall/latest/set-up/open-source/) |
| Auto-assign alert to specific user   | No                           | Yes - per-monitor on-call policy     | Cloud IRM only                                     |
| JSM native integration               | Yes - native (v2.3.2, [PR #6830](https://github.com/louislam/uptime-kuma/pull/6830)) | No native | OSS: No. Cloud IRM: Jira project issues only, not JSM Ops Alerts |
| Slack native integration             | Yes - native                 | Yes - native workspace connection    | Yes - native contact point in OSS alerting         |
| GitHub Issues native integration     | No                           | No                                   | Cloud IRM: Yes. OSS alerting: No                   |
| Built-in notification channels       | [90+ native](https://github.com/louislam/uptime-kuma/tree/master/src/components/notifications) + [78+ via Apprise](https://github.com/louislam/uptime-kuma/wiki/Notification-Methods) | ~8-10 (Slack, Teams, Email, Discord, Telegram) | ~20 contact point types in OSS alerting |
| Logs / Metrics / Traces              | No                           | Yes - ClickHouse + OTel              | Yes - Loki + Mimir + Tempo (LGTM stack)            |
| Containers required (self-hosted)    | 1                            | 7                                    | 1 (OSS only); full LGTM stack = 4+                |
| RAM (self-hosted, minimum)           | ~150 MB                      | ~2-4 GB                              | ~250 MB (OSS only)                                 |

## Monitoring Capabilities

| Feature                   | Uptime Kuma               | OneUptime                                    | Grafana                                               |
| ------------------------- | ------------------------- | -------------------------------------------- | ----------------------------------------------------- |
| HTTP / HTTPS              | Yes - built-in            | Yes - built-in                               | Via [Blackbox Exporter](https://github.com/prometheus/blackbox_exporter) + Prometheus or [Cloud Synthetics](https://grafana.com/docs/grafana-cloud/testing/synthetic-monitoring/) |
| Ping (ICMP)               | Yes - built-in            | Yes - built-in                               | Via [Blackbox Exporter](https://github.com/prometheus/blackbox_exporter) |
| TCP Port                  | Yes - built-in            | Yes - built-in                               | Via [Blackbox Exporter](https://github.com/prometheus/blackbox_exporter) |
| DNS                       | Yes - built-in            | Yes - built-in                               | Via [Blackbox Exporter](https://github.com/prometheus/blackbox_exporter) |
| SSL Certificate           | Yes - basic expiry check  | Yes - expiry days, validity, degraded threshold, self-signed detection | Via [Blackbox Exporter](https://github.com/prometheus/blackbox_exporter) (`ssl_expiry_in_days` metric only) |
| Domain expiry             | Yes - notification with configurable advance days | Yes - [Domain Monitor](https://oneuptime.com/docs/en/monitor/domain-monitor) | No built-in                                           |
| Docker containers         | Yes                       | Yes - agent-based                            | Via cAdvisor + Prometheus                             |
| Kubernetes                | No                        | Yes - Helm agent                             | Yes - native Kubernetes Monitoring (Cloud or OSS)     |
| Server / VM               | No                        | Yes - agent                                  | Yes - via Node Exporter + Prometheus                  |
| Incoming request (push)   | Yes                       | Yes                                          | No direct equivalent                                  |
| Logs / Metrics / Traces   | No                        | Yes - OpenTelemetry, ClickHouse-backed       | Yes - Loki (logs), Mimir/Prometheus (metrics), Tempo (traces) |
| Multiple probe locations  | No - single instance      | Yes - custom probes per region               | Cloud Synthetics only (not self-hosted OSS)           |
| Synthetic browser tests   | No                        | No                                           | Yes - Cloud only (k6 browser, Synthetics)             |

## Notifications and Integrations

| Integration                        | Uptime Kuma                  | OneUptime                         | Grafana OSS Alerting (v13)                        |
| ---------------------------------- | ---------------------------- | --------------------------------- | ------------------------------------------------- |
| Slack                              | Yes - native                 | Yes - native workspace connection | Yes - native contact point                        |
| Microsoft Teams                    | Yes - native                 | Yes - native workspace connection | Yes - native contact point                        |
| Email / SMTP                       | Yes - native                 | Yes - native                      | Yes - native contact point                        |
| Discord                            | Yes - native                 | Yes - workflow component          | Yes - native contact point                        |
| Telegram                           | Yes - native                 | Yes - workflow component          | Yes - native contact point                        |
| PagerDuty                          | Yes - native                 | No native integration             | Yes - native contact point                        |
| OpsGenie                           | Yes - native                 | No native integration             | Yes - native contact point                        |
| Jira Service Management (Ops)      | Yes - native (v2.3.2, [PR #6830](https://github.com/louislam/uptime-kuma/pull/6830)) | No native | OSS: No. Cloud IRM: No (Jira integration creates project issues, not JSM Ops Alerts) |
| Jira Software (project issues)     | No native integration        | No native integration             | OSS: No. Cloud IRM: Yes - [native Jira integration](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/integrations/dev-and-operations/jira/) |
| GitHub Issues                      | No native integration        | No native integration             | OSS: No. Cloud IRM: Yes - [native GitHub integration](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/integrations/dev-and-operations/github/) |
| Grafana OnCall                     | Yes - native                 | No native integration             | OSS: No (OnCall archived). Cloud IRM: built-in    |
| Splunk On-Call (VictorOps)         | Yes - native                 | No native integration             | Yes - native contact point                        |
| Apprise ([78+ services](https://github.com/caronc/apprise/wiki)) | Yes - [built-in](https://github.com/louislam/uptime-kuma/wiki/Notification-Methods) | No | No |
| SMS (Twilio)                       | Yes - native                 | Yes - via on-call policy          | No built-in; needs custom webhook                 |
| Webhook (generic)                  | Yes                          | Yes                               | Yes - contact point                               |

**Grafana OSS alerting contact points** ([v13 docs](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/)): AlertManager, DingDing, Discord, Email, Google Hangouts Chat, Kafka REST Proxy, Line, Microsoft Teams, OpsGenie, PagerDuty, Prometheus Alertmanager, Pushover, Sensu, Slack, Telegram, Threema, VictorOps, Webhook, Weixin (WeCom).

**Grafana Cloud IRM dev-and-ops integrations ([docs](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/integrations/dev-and-operations/)):** GitHub (link incidents with repos and issues), Jira (project issue creation, not JSM Ops Alerts), StatusPage (status updates). ServiceNow is not a listed native IRM integration. Cloud IRM only, not available in self-hosted Grafana OSS.

## Incident Management and Alert Routing

Uptime Kuma has no incident management concept. When a monitor goes down, it fires all configured notification channels simultaneously. There is no assignment, acknowledgement, escalation, or ownership within the tool itself.

Grafana OSS has no incident management. Alerts fire to notification channels. Incident management requires Grafana Cloud IRM.

OneUptime has a full incident lifecycle with pre-configured routing per monitor, self-hosted.

### Incident Management

| Feature                                       | Uptime Kuma | OneUptime                                             | Grafana OSS     | Grafana Cloud IRM                    |
| --------------------------------------------- | ----------- | ----------------------------------------------------- | --------------- | ------------------------------------ |
| Auto-create incidents from monitors           | No          | Yes                                                   | No              | Yes                                  |
| Incident severity / title / description       | No          | Yes - dynamic templates using monitor response data   | No              | Yes                                  |
| Auto-assign to a specific user on alert fire  | No          | Yes - on-call policy linked per monitor               | No              | Yes                                  |
| Different assigned users per monitor          | No          | Yes - each monitor can have its own on-call policy    | No              | Yes                                  |
| Escalation if no acknowledgement in N minutes | No          | Yes - layered escalation within on-call policy        | No              | Yes                                  |
| Incident acknowledgement                      | No          | Yes - UI, mobile app, or notification reply           | No              | Yes                                  |
| Incident timeline and notes                   | No          | Yes                                                   | No              | Yes                                  |
| Post-mortem / root cause tracking             | No          | Yes                                                   | No              | Yes                                  |
| Multi-user collaboration on incidents         | No          | Yes                                                   | No              | Yes                                  |

### On-Call and Alert Routing

| Feature                              | Uptime Kuma | OneUptime | Grafana OSS | Grafana Cloud IRM |
| ------------------------------------ | ----------- | --------- | ----------- | ----------------- |
| On-call schedules (time-based)       | No          | Yes       | No          | Yes               |
| Layered escalation policies          | No          | Yes       | No          | Yes               |
| Phone call routing via Twilio        | No          | Yes       | No          | Yes               |
| Per-monitor on-call policy           | No          | Yes       | No          | Yes               |
| Acknowledgement tracking             | No          | Yes       | No          | Yes               |
| On-call duty audit log               | No          | Yes       | No          | Yes               |
| Self-hosted option for on-call       | No          | Yes       | No          | No - cloud only   |

**Grafana OnCall OSS note:** The open source on-call product ([`grafana/oncall`](https://github.com/grafana/oncall)) was [archived on March 24, 2026](https://grafana.com/docs/oncall/latest/set-up/open-source/). The repository is read-only. Active development moved to [Grafana Cloud IRM](https://grafana.com/products/cloud/irm/). Self-hosted on-call is no longer a supported path with Grafana.

OneUptime on-call policy routing example (pre-configured per monitor, [docs](https://oneuptime.com/docs/on-call-duty/on-call-policy)):

```
Monitor (/health) --> On-Call Policy: "Backend"
  Layer 1: User A          -- wait 5 min, no ack
  Layer 2: Team "Backend"  -- wait 10 min, no ack
  Layer 3: User B (lead)   -- fallback

Monitor (SSL: demo.ohc.network) --> On-Call Policy: "Infra"
  Layer 1: User C          -- wait 5 min, no ack
  Layer 2: User D (lead)   -- fallback
```

## Jira, Slack, and GitHub Issues

| Capability                                                 | Uptime Kuma          | OneUptime                    | Grafana OSS          | Grafana Cloud IRM         |
| ---------------------------------------------------------- | -------------------- | ---------------------------- | -------------------- | ------------------------- |
| Slack - send alert notification                            | Yes - native         | Yes - native                 | Yes - native         | Yes - native              |
| Slack - initiate incident from Slack                       | No                   | No                           | No                   | Yes                       |
| Slack - acknowledge / resolve from Slack message           | No                   | No                           | No                   | Yes                       |
| JSM Ops Alerts - create alert on monitor down              | Yes - native (v2.3.2) | No native                   | No native            | No - Jira integration creates project issues, not JSM Ops Alerts |
| JSM Ops Alerts - auto-close on recovery                   | Yes - native         | No native                    | No native            | No                        |
| Jira Software - create project issue from incident         | No                   | No                           | No                   | Yes - [native Jira integration](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/integrations/dev-and-operations/jira/) |
| GitHub Issues - create issue from incident                 | No                   | No                           | No                   | Yes - [native GitHub integration](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/integrations/dev-and-operations/github/) |
| ServiceNow integration                                     | No                   | No                           | No                   | No - not a listed IRM integration ([IRM dev-and-ops integrations](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/integrations/dev-and-operations/)) |

**Uptime Kuma JSM:** Connects to `api.atlassian.com/jsm/ops/api/{cloudId}/v1/alerts` ([JSM Ops Alerts API](https://developer.atlassian.com/cloud/jira-service-management/rest/api-group-alerts/)). Creates a P1-P5 ops alert on monitor DOWN, auto-closes on UP. This is the JSM on-call alerting layer only - not Jira Software project board tickets.

**Grafana Cloud IRM ITSM:** Native integrations with [Jira](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/integrations/dev-and-operations/jira/) (project issue creation and task management), [GitHub](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/integrations/dev-and-operations/github/) (link incidents with repositories and issues), and [StatusPage](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/integrations/dev-and-operations/statuspage/) (status updates). Jira here refers to project issues, not JSM Ops Alerts (separate API and alerting layer). ServiceNow has no native IRM integration. These integrations are Cloud IRM only and not available in self-hosted Grafana OSS.

**Grafana OSS alerting:** No native JSM, GitHub Issues, or Jira Software [contact point](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/). The built-in webhook contact point can be configured manually to call the JSM API, but this is not a native integration.

## Infrastructure Requirements

| Item              | Uptime Kuma                   | OneUptime (this repo)                                         | Grafana OSS (minimal)             |
| ----------------- | ----------------------------- | ------------------------------------------------------------- | --------------------------------- |
| Containers        | 1                             | 7 (app, probe, ingress, postgres, clickhouse, redis, fastapi) | 1 (Grafana only)                  |
| Database          | SQLite - default              | PostgreSQL 18 + ClickHouse 26.4 + Redis 8.2                  | SQLite or PostgreSQL (self-host)  |
| Minimum RAM       | ~150 MB                       | ~2-4 GB (ClickHouse alone needs ~1 GB)                        | ~250 MB (OSS only)                |
| Storage growth    | Minimal - single DB file      | High - ClickHouse grows with log and metric data              | Low to medium (depends on data sources used) |
| Setup time        | ~5 minutes                    | ~30-60 minutes                                                | ~10-15 minutes                    |
| HTTP monitoring   | Built-in                      | Built-in                                                      | Requires Blackbox Exporter setup  |
| Incident mgmt     | Not available                 | Self-hosted, included                                         | Requires Grafana Cloud account    |

**Grafana full LGTM stack** ([Loki](https://grafana.com/oss/loki/) + Grafana + [Tempo](https://grafana.com/oss/tempo/) + [Mimir](https://grafana.com/oss/mimir/), self-hosted): ~4-6 containers, ~2-4 GB RAM, significant storage. Comparable in complexity to the OneUptime stack.

## Pricing

| Tier                          | Uptime Kuma       | OneUptime              | Grafana OSS            | Grafana Cloud IRM         |
| ----------------------------- | ----------------- | ---------------------- | ---------------------- | ------------------------- |
| Free self-hosted              | Yes - fully free  | Yes - [Apache 2.0](https://github.com/OneUptime/oneuptime/blob/master/LICENSE), self-hosted | Yes - AGPLv3, free     | No - cloud account needed |
| Free cloud                    | No cloud offering | No cloud offering      | Yes - 3 active users   | Yes - 3 IRM users/month   |
| Paid cloud                    | No                | No                     | [$8/active user/month + $19/month platform fee](https://grafana.com/pricing/) | [$20/active IRM user/month + $19/month platform fee](https://grafana.com/pricing/) |
| Enterprise (self-hosted)      | No                | No                     | [Custom pricing, annual license](https://grafana.com/pricing/) | No - IRM is cloud-only |
| Incident management cost      | Free (no feature) | Free (self-hosted, Apache 2.0) | Free (no feature in OSS) | [$20/user/month + platform fee](https://grafana.com/pricing/) |
| Minimum paid spend            | $0                | $0                     | [$19/month Pro platform fee](https://grafana.com/pricing/) | [$19/month Pro platform fee](https://grafana.com/pricing/) |

## Recommendation

| Requirement                                           | Uptime Kuma         | OneUptime                               | Grafana OSS         | Grafana Cloud IRM                    |
| ----------------------------------------------------- | ------------------- | --------------------------------------- | ------------------- | ------------------------------------ |
| FastAPI /health endpoint monitor                      | Yes                 | Yes                                     | Via Blackbox Exporter | Via Blackbox Exporter or Cloud Synthetics |
| SSL certificate monitor with 30-day warning           | Partial - expiry only | Yes - full degraded/offline thresholds | Via Blackbox Exporter (expiry metric) | Cloud Synthetics only |
| Auto-create incident when monitor fires               | No                  | Yes                                     | No                  | Yes                                  |
| Auto-assign incident to specific user                 | No                  | Yes                                     | No                  | Yes                                  |
| Different assignees per monitor type                  | No                  | Yes                                     | No                  | Yes                                  |
| Escalate to next user if no acknowledgement           | No                  | Yes                                     | No                  | Yes                                  |
| JSM integration - native, no bridge                   | Yes                 | No                                      | No (OSS)            | No - Jira project issues only, not JSM Ops Alerts |
| Jira Software issue creation - native                 | No                  | No                                      | No (OSS)            | Yes                                  |
| GitHub Issues creation - native                       | No                  | No                                      | No (OSS)            | Yes                                  |
| Slack notifications                                   | Yes                 | Yes                                     | Yes                 | Yes                                  |
| Self-hosted - no monthly cost                         | Yes                 | Yes                                     | Yes (OSS alerting only) | No - cloud only               |
| On-call scheduling - self-hosted                      | No                  | Yes                                     | No (OnCall archived) | No - cloud only                    |

**If JSM Ops Alerts + GitHub Issues + Jira Software project tickets are all required:** No single tool covers all three. Uptime Kuma covers JSM Ops Alerts natively (self-hosted, free). Grafana Cloud IRM covers Jira project issues + GitHub Issues natively (cloud only, $20/user/month after 3 free). There is no self-hosted option that covers all three in one tool.

**If JSM native only (no GitHub Issues, no Jira Software) and self-hosted is required:** Uptime Kuma covers JSM natively. The trade-off is losing incident management, on-call routing, and user assignment.

**If incident lifecycle and user assignment are the priority and JSM is not a hard requirement:** OneUptime covers the full incident lifecycle and user assignment self-hosted at no cost. JSM and GitHub Issues have no native support, but Slack does.

**If you already have a Grafana stack for metrics/logs** and want to add alerting without a second monitoring tool: Grafana OSS alerting (Alertmanager) handles Slack, Teams, PagerDuty, OpsGenie natively. Add Grafana Cloud IRM on top for incident management - 3 users free, $20/user/month after that.
