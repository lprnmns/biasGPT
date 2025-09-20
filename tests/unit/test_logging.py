from packages.telemetry.logging import log


def test_log_output_contains_fields(capsys):
    line = log("info", "hello", foo="bar")
    captured = capsys.readouterr()
    assert "hello" in line
    assert "foo" in line
    assert "hello" in captured.out
