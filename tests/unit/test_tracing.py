from packages.telemetry.tracing import generate_trace_id, get_trace_id


def test_trace_id_generation():
    trace_a = generate_trace_id()
    trace_b = generate_trace_id()
    assert trace_a
    assert trace_b
    assert trace_a != trace_b


def test_trace_id_context():
    trace = generate_trace_id()
    assert get_trace_id() == trace
