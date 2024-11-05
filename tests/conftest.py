import pytest

RUN_NAME = "exp"
WORKFLOW_NAME = "my_workflow"
FLOW_CONTENT = """
#!jinja2

## PREPARE JINJA2 to use medfs - DO NOT TOUCH
{% set ROOT_DIR = environ['ROOT_DIR'] %}
{% from "__python__.sys" import path %}
{% do path.insert(1, ROOT_DIR) %}

## Workflow
{% set START_DATE = environ['START_DATE'] %}
{% set END_DATE = environ['END_DATE'] %}

[meta]
    title = Parametrized Workflow

[task parameters]
{% for tag, tasks in task_with_tags(TASK_CONFIG).items() %}
    {{tag}} = {{tasks}}
{% endfor %}

[scheduling]
    initial cycle point = {{START_DATE}}
    final cycle point = {{END_DATE}}

    [[graph]]
        R1 = "foo => bar"

[runtime]
    [[root]]
        platform = mye_lsf
        [[[environment]]]
            START_DATE = {{START_DATE}}
            END_DATE = {{END_DATE}}
            CYCLE_POINT = $(echo $CYLC_TASK_CYCLE_POINT | cut -dT -f1)
            INITIAL_CYCLE_POINT = $(echo $CYLC_WORKFLOW_INITIAL_CYCLE_POINT | cut -dT -f1)

    [[foo]]
        script = "echo FOO"
{% for name, value in task_directives("PARALLEL", TASK_CONFIG).items() %}
    {% if value|length > 0 %}
        {{name}} = {{value}}
    {% endif %}
{% endfor %}


    [[bar]]
        script = "echo BAR"
{% for name, value in task_directives("PARALLEL", TASK_CONFIG).items() %}
    {% if value|length > 0 %}
        {{name}} = {{value}}
    {% endif %}
{% endfor %}

"""


@pytest.fixture
def cylc_run(monkeypatch, tmp_path):
    """Define cylc run and export value as CYLC_RUN_DIR"""
    cylc_run_path = tmp_path / "cylc-run"
    monkeypatch.setenv("CYLC_RUN_DIR", cylc_run_path.as_posix())

    return cylc_run_path


@pytest.fixture
def cylc_src(monkeypatch, tmp_path):
    """Define cylc run and export value as CYLC_RUN_DIR"""
    cylc_src_path = tmp_path / "cylc-src"
    monkeypatch.setenv("CYLC_SRC_DIR", cylc_src_path.as_posix())

    return cylc_src_path


@pytest.fixture
def flow_cylc(tmp_path):
    f = tmp_path / "my_workflow.cylc"
    f.write_text(FLOW_CONTENT)
    return f
