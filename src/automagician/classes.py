from dataclasses import dataclass
from enum import IntEnum
from typing import Literal

try:
    import fabric  # type: ignore

    @dataclass
    class SshScp:
        ssh: fabric.connection.Connection
        scp: fabric.transfer.Transfer

    @dataclass
    class SSHConfig:
        config: Literal["NoSSH"] | SshScp

except ImportError:

    @dataclass
    class SSHConfig:  # type: ignore
        config: Literal["NoSSH"]


class JobStatus(IntEnum):
    """A enum storing the status of a job

    Converged = 0
    Incomplete = 1
    Error = 2
    Running = -1
    NotFound = -10"""

    CONVERGED = 0
    INCOMPLETE = 1
    ERROR = 2
    RUNNING = -1
    NOT_FOUND = -10


class Machine(IntEnum):
    FRI_ODEN = 0
    HALIFAX_ODEN = 1
    STAMPEDE2_TACC = 2
    FRONTERRA_TACC = 3
    LS6_TACC = 4
    UNKNOWN = -1


@dataclass
class OptJob:
    """A class to represent an optomization job

    status
    home_machine
      The machine this job is on
    last_on
      The machine this job was last ran on
    """

    status: JobStatus
    home_machine: Machine
    last_on: Machine


@dataclass
class DosJob:
    """Density optomization job

    opt_id
      The id of the optomization job this is connected to
    sc_status
      The status of the optomization job this is connected to
    dos_status
        The status of the job
    sc_last_on
      The machine the of the optomization job this is connected to
    dos_last_on
      The machine that this job was connected to
    """

    opt_dir = None
    opt_id: int | Literal[-1]
    sc_status: JobStatus
    dos_status: JobStatus
    sc_last_on: Machine
    dos_last_on: Machine


@dataclass
class WavJob:
    """A job ran specifically to obtain a WAVECAR
    opt_id
      The id of the optomization job this is connected to
    wav_status
      The status of the job
      0 = done
      1 = nonexistent or unconverged (Unclear) TODO: Get what this means
      2 = error
      -1 = running
    wav_last_on
      The machine that this job was connected to"""

    opt_dir = None
    opt_id: int | Literal[-1]
    wav_status: JobStatus
    wav_last_on: Machine


@dataclass
class GoneJob:
    """A record of jobs that can no longer be found"""

    old_dir: str
    status: JobStatus
    home_machine: Machine
    last_on: Machine


class JobLimitError(Exception):
    """What happens if you submit too many jobs"""

    def __init__(self) -> None:
        pass
