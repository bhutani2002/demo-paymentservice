# Architecture — demo-paymentservice

## Design Intent

This service handles payment processing, retries, and refunds for a
multi-tenant merchant platform.

## Core Principles

1. **Config-driven** — all tunable values live in `Config`. No magic numbers in business logic.
2. **Resilient** — circuit breaker prevents cascade failures; retry handler manages transient errors.
3. **Idempotent** — duplicate payment requests are safe; same key returns cached result.
4. **Exception-safe** — all errors propagate as typed `ServiceException` subclasses.

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `config.py` | Single source of truth for all configurable values |
| `exceptions.py` | Typed exception hierarchy |
| `models.py` | Dataclasses for requests and results |
| `retry_handler.py` | Exponential backoff with jitter |
| `payment_processor.py` | Orchestrates payment flow: idempotency → circuit breaker → retry → gateway |
| `refund_service.py` | Refund processing with duplicate protection |

## Team Decisions

See `review-artifacts/memory/team-decisions.json` for recorded architectural decisions.
ReviewGuard enforces these on every PR.
