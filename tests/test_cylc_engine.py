import shutil

import pytest
from cylc import CylcEngine, cylc_util
from tests.conftest import RUN_NAME, WORKFLOW_NAME


@pytest.fixture
def cylc_engine(
    flow_cylc, test_home, monkeypatch
):
    monkeypatch.setenv("HOME", test_home)
    return CylcEngine(flow_cylc)


@pytest.mark.parametrize(
    "run_name,expected",
    [("exp", "exp1"), ("exp10", "exp11"), ("exp1", "exp2"), ("1exp1", "1exp2")],
)
def test_increase_index_in_str(run_name, expected):
    s = cylc_util.increase_index_in_str_by_one(run_name)
    assert s == expected


def test_init(cylc_engine):
    assert isinstance(cylc_engine, CylcEngine)


def test_workflow_name(cylc_engine):
    assert cylc_engine.workflow_name == WORKFLOW_NAME


def test_id(cylc_engine):
    assert cylc_engine.id == f"{WORKFLOW_NAME}/{RUN_NAME}"


@pytest.mark.parametrize(
    "run_name,expected",
    [("my_run10", "my_workflow/my_run10"), ("my_run", "my_workflow/my_run")],
)
def test_id_user_run_name(flow_cylc, run_name, expected):
    engine = CylcEngine(flow_cylc, **{"CYLC_RUN_NAME": run_name})
    assert engine.id == expected


def test_contact_path(cylc_engine, cylc_run, test_home):
    expected = cylc_run / WORKFLOW_NAME / RUN_NAME / ".service" / "contact"
    expected.parent.mkdir(parents=True, exist_ok=True)
    result = cylc_engine.path_to_contact

    assert result.as_posix() == expected.as_posix()
    print(result.as_posix())


def test_workflow_run_path(cylc_engine, cylc_run):
    workflow_id_path = cylc_run / WORKFLOW_NAME / RUN_NAME
    workflow_id_path.mkdir(parents=True, exist_ok=True)

    result = cylc_engine.cylc_run_directory

    assert result.is_dir()
    assert result.name + "cylc-run"
    assert result.samefile(workflow_id_path)


def test_cylc_src_base_path(cylc_engine, cylc_src):
    expected = cylc_src / WORKFLOW_NAME
    expected.mkdir(parents=True, exist_ok=True)

    result = cylc_engine.cylc_src_workflow_directory

    assert result.is_dir()
    assert result.name == WORKFLOW_NAME
    assert result.samefile(expected)


def test_cylc_src_workflow(cylc_engine, cylc_src):
    expected = cylc_src / WORKFLOW_NAME / "flow.cylc"
    expected.parent.mkdir(parents=True, exist_ok=True)
    expected.touch()

    result = cylc_engine.cylc_src_workflow

    assert result.is_file()
    assert result.samefile(expected)


def test_link_flow_to_cylc_src(cylc_engine, flow_cylc, cylc_src):
    expected = cylc_src / WORKFLOW_NAME / "flow.cylc"

    cylc_engine.cylc_src_workflow.unlink(missing_ok=True)
    assert not expected.is_file()

    cylc_engine.link_flow_to_cylc_src()

    assert expected.is_file()
    assert expected.samefile(flow_cylc)


def test_link_flow_to_cylc_src_with_conflict(
    tmp_path, cylc_engine, flow_cylc, cylc_src
):
    expected = cylc_src / WORKFLOW_NAME / "flow.cylc"
    expected.unlink(missing_ok=True)

    other_flow = tmp_path / "other.cylc"
    other_flow.touch()

    expected.parent.mkdir(parents=True, exist_ok=True)
    expected.symlink_to(other_flow)

    with pytest.raises(ValueError):
        cylc_engine.link_flow_to_cylc_src()


@pytest.mark.parametrize(
    "run_names,expected",
    [
        (["exp", "exp1"], "exp2"),
        (["exp"], "exp1"),
        ([], "exp"),
        (["exp", "exp1", "exp2"], "exp3"),
        (["exp", "exp1", "exp9"], "exp10"),
        (["exp10"], "exp11"),
        (["exp_10"], "exp_11"),
    ],
)
def test_run_name_extension(cylc_engine, cylc_run, run_names, expected):
    workflow_run_base_path = cylc_run / WORKFLOW_NAME
    shutil.rmtree(workflow_run_base_path, ignore_errors=True)
    for run_name in run_names:
        (workflow_run_base_path / run_name).mkdir(parents=True, exist_ok=True)
    result = cylc_engine.run_name_extension()
    assert result == expected


def test_get_run_name_to_install(cylc_engine):
    assert cylc_engine.get_run_name_to_install() == RUN_NAME


@pytest.mark.parametrize(
    "run_names,expected",
    [
        (["exp", "exp1"], "exp2"),
        (["exp"], "exp1"),
        ([], "exp"),
        (["exp", "exp1", "exp2"], "exp3"),
        (["exp", "exp1", "exp9"], "exp10"),
        (["exp10"], "exp11"),
        (["exp_10"], "exp_11"),
    ],
)
def test_get_run_name_to_install_with_extend(flow_cylc, cylc_run, run_names, expected):
    cylc_engine = CylcEngine(flow_cylc, **{"CYLC_EXTEND": True})
    workflow_run_base_path = cylc_run / WORKFLOW_NAME
    shutil.rmtree(workflow_run_base_path, ignore_errors=True)
    for run_name in run_names:
        (workflow_run_base_path / run_name).mkdir(parents=True, exist_ok=True)

    assert cylc_engine.run_name_extension() == expected
