"""Trace context helper."""

from __future__ import annotations

import contextvars
import uuid

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")


def generate_trace_id() -> str:
    trace = uuid.uuid4().hex
    trace_id_var.set(trace)
    return trace


def get_trace_id() -> str:
    value = trace_id_var.get()
    if not value:
        return generate_trace_id()
    return value


__all__ = ["generate_trace_id", "get_trace_id"]
