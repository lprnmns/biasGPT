import pathlib


def test_ci_workflow_exists():
    workflow = pathlib.Path(".github/workflows/ci.yml")
    assert workflow.exists(), "ci.yml should exist"


def test_makefile_targets():
    makefile = pathlib.Path("Makefile")
    content = makefile.read_text()
    assert "test:" in content
