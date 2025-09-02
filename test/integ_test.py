import os

import pytest

import automagician.main


def test_automagician_lockfile_present():
    lockfile_path = "/tmp/automagician/" + os.environ["USER"] + "-lock"
    lockfile = open(lockfile_path, "w")
    lockfile.write("MockLockfile")
    lockfile.close()
    with pytest.raises(SystemExit):
        automagician.main.main()
    os.remove(lockfile_path)
    assert True
