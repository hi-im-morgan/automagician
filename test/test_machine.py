from automagician.classes import Machine, SSHConfig
from automagician.machine import *
import logging

def test_is_oden():
    assert is_oden(Machine.FRI_ODEN)
    assert is_oden(Machine.HALIFAX_ODEN)
    assert not is_oden(Machine.UNKNOWN)
    assert not is_oden(Machine.FRONTERRA_TACC)
    assert not is_oden(Machine.LS6_TACC)
    assert not is_oden(Machine.STAMPEDE2_TACC)


def test_is_tacc():
    assert not is_tacc(Machine.FRI_ODEN)
    assert not is_tacc(Machine.HALIFAX_ODEN)
    assert not is_tacc(Machine.UNKNOWN)
    assert is_tacc(Machine.FRONTERRA_TACC)
    assert is_tacc(Machine.LS6_TACC)
    assert is_tacc(Machine.STAMPEDE2_TACC)

def test_ssh_scp_init():
    logger = logging.Logger("test")
    ssh_config = ssh_scp_init(
        machine = get_machine_number(),
        home_dir = os.environ["HOME"],
        balance = True,
        logger = logger
    )

    assert isinstance(ssh_config, SSHConfig)
