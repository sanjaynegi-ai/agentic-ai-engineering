# Observability standard

Observability spans application events, agent traces, infrastructure metrics, behavioral evaluations, and incident response. No single signal is sufficient.

## Structured application events

Emit JSON-compatible events to standard output so local terminals, Docker, ECS `awslogs`, and Kubernetes collectors can process the same stream. Recommended fields:

- `timestamp`, `level`, `event`, `service`, `environment`
- `correlation_id`, `session_id` or hashed user/session identifier
- framework/implementation, prompt version, model, agent name
- tool/handoff/guardrail name, validated argument categories, duration and status
- turn/tool-call counts, token usage, estimated cost and retry count
- final status and exception type

Do not log API keys, authorization headers, cookies, full personal data, raw secrets, or unrestricted prompt/tool payloads. Redact at event creation rather than relying only on downstream filters.

## Traces, metrics, and evaluations

- **Trace:** explains one execution across model calls, tools, handoffs, and guardrails.
- **Metric:** reveals aggregate availability, latency, capacity, cost, and error trends.
- **Evaluation:** tests whether behavior remains useful, scoped, grounded, and safe.

Use a correlation ID to connect these signals. Run deterministic evaluations before and after deployment changes; do not infer agent quality from HTTP uptime alone.

## Environment operations

- Local/Docker: terminal logs, `docker logs --follow`, `docker stats`.
- ECS: CloudWatch log group, Container Insights, ECS CPU/memory alarms, ALB health/latency/5xx metrics, and the Terraform-created dashboard.
- EKS: probes, `kubectl logs`, events, rollout status, pod metrics, and the cluster owner's centralized OpenTelemetry/Container Insights installation.
- OpenAI Agents SDK: trace model/agent/tool/handoff/guardrail spans while respecting sensitive-data controls and retention policy.

The exact commands, Terraform outputs, minimum production signals, and incident loop are documented in [`projects/README.md`](../projects/README.md#12-observe-and-operate-the-project).

## Alerting and retention

Route actionable alarms to an approved incident channel. The Terraform baseline creates alarms without notification actions; connect them to an SNS topic in a real environment. Avoid alerts that have no owner or response playbook.

CloudWatch application logs default to 14-day retention. Adjust retention to organizational policy and cost constraints. Trace and evaluation datasets may contain model inputs/outputs, so apply access control, redaction, residency, and deletion requirements separately from infrastructure logs.
