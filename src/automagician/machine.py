import datetime
import logging
import os
import re
import socket
import subprocess
from os.path import exists
from typing import NoReturn

import automagician.constants as constants
from automagician.classes import Machine, SSHConfig

no_fabric = False
try:
    import fabric  # type: ignore

    from automagician.classes import SshScp
except ImportError:
    print("fabric unavailable")
    no_fabric = True


def get_machine_number() -> Machine:
    """Returns the number of the machine that is currently logged in.
    Args:
      None
    Returns:
        The currently logged on machine, or Machine.UNKNOWN if not known
        if logged on to fri.oden.utexas.edu returns Machine.FRI_ODEN
        if logged on to halifax.oden.utexas.edu returns Machine.HALIFAX_ODEN
        if logged on to stempede2.tacc.utexas.edu returns Machine.STAMPEDE2_TACC
        if logged on to fronterra.tacc.utexas.edu returns Machine.FRONTERRA_TACC
        if logeed on to ls6.tacc.utexas.edu returns Machine.LS6_TACC
    """
    rm_login_node = re.compile(r"login[0-3]\.")
    machine_name = rm_login_node.sub("", socket.gethostname())
    return {
        "fri.cm.utexas.edu": Machine.FRI_ODEN,
        "halifax.cm.utexas.edu": Machine.HALIFAX_ODEN,
        "stampede2.tacc.utexas.edu": Machine.STAMPEDE2_TACC,
        "frontera.tacc.utexas.edu": Machine.FRONTERRA_TACC,
        "ls6.tacc.utexas.edu": Machine.LS6_TACC,
    }.get(machine_name, Machine.UNKNOWN)


def ssh_scp_init(
    machine: Machine, home_dir: str, balance: bool, logger: logging.Logger
) -> SSHConfig:
    """Initalizes ssh and sets the no_ssh varable appropately

    Additonally opens up a scp connection
    Args:
      machine: The machine nubmer that is currently running
      home_dir: The users home directoy
      balance: if balance was set up in parser options
    Returns:
      a ssh config object
      no_ssh is set to true, iff fabric could not be imported, balance was not set, or fri_halifax keys did not work
    """
    # unused = 0

    if not balance:
        return SSHConfig(config="NoSSH")

    if machine < 2:
        hostname = get_machine_name(Machine(1 - machine))
        if no_fabric:
            logger.warning("you need fabric for ssh to work")
            return SSHConfig(config="NoSSH")
        else:
            try:
                ssh = fabric.Connection(
                    user=os.environ["USER"],
                    host=hostname,
                    connect_kwargs={
                        "key_filename": home_dir + "/.ssh/automagician_id_rsa"
                    },
                    config=fabric.config.Config(overrides={"warn": True}),
                )
                scp = fabric.transfer.Transfer(ssh)
                ssh.run("hostname")
            except Exception:
                logger.warning("you need fri-halifax keys for ssh to work")
                return SSHConfig(config="NoSSH")
    return SSHConfig(config=SshScp(ssh=ssh, scp=scp))


def get_machine_name(machine_number: Machine) -> str:
    """Returns the name of the machine nane, or localhost if not found
    Args:
      machine_number (int): The number of the machine
    Returns:
      str: the name of the machine connected with machine_number, or localhost if none are connected
        if 0 returns fri.oden.utexas.edu
        if 1 returns halifax.oden.utexas.edu
        if 2 returns stempede2.tacc.utexas.edu
        if 3 returns frontera.tacc.utexas.edu
        if 4 returns ls6.tacc.utexas.edu
        if none of the above returns localhost
    """
    return {
        Machine.FRI_ODEN: "fri.oden.utexas.edu",
        Machine.HALIFAX_ODEN: "halifax.oden.utexas.edu",
        Machine.STAMPEDE2_TACC: "stampede2.tacc.utexas.edu",
        Machine.FRONTERRA_TACC: "frontera.tacc.utexas.edu",
        Machine.LS6_TACC: "ls6.tacc.utexas.edu",
    }.get(machine_number, "localhost")


def write_lockfile(ssh_config: SSHConfig, machine: Machine) -> None:
    """Creates a lockfile to stop two automagicians from treading on each other
    Args:
      None
    Returns:
      Nothing
    Modifies:
      machine
        Creates the lockdir directory if it dosent exist, and sets permissions to 777.
        if a lockfile does not exist in the lockdir directory creates a lockfile

        lockfile
          Contains USER, machine, process PID, and the time started at
    Exits:
      If the lockfile already exists exits the program
    """
    logger = logging.getLogger()
    if not os.path.isdir(constants.LOCK_DIR):
        os.makedirs(constants.LOCK_DIR)
        subprocess.run(["chmod", "777", constants.LOCK_DIR])

    if machine < 2 and ssh_config.config != "NoSSH":
        if not ssh_config.config.ssh.run(
            "test -d " + constants.LOCK_DIR, warn=True, hide=True
        ).ok:
            ssh_config.config.ssh.run("mkdir -p " + constants.LOCK_DIR)

    if exists(constants.LOCK_FILE):
        logger.error(
            "it looks like you already have an instance of automagician running--please wait for it to finish. thank you! :)"
        )
        logger.error("other automagician process's details:")
        subprocess.call(["cat", constants.LOCK_FILE])
        logger.error(
            f"if you'd like to override the lock, you can delete {constants.LOCK_FILE} and rerun your process."
        )
        exit()
    elif (
        machine < 2
        and ssh_config.config != "NoSSH"
        and ssh_config.config.ssh.run(
            "test -e " + constants.LOCK_FILE, warn=True, hide=True
        ).ok
    ):
        logger.error(
            "it looks like you already have a remote instance of automagician running--please wait for it to finish. thank you! :)",
        )
        logger.error("other automagician process's details:")
        ssh_config.config.ssh.run("cat " + constants.LOCK_FILE)
        logger.error(
            f"if you'd like to override the lock, you can delete {constants.LOCK_FILE} on the remote machine and rerun your process",
        )
        exit()
    else:
        lockstring = f"user: {os.environ.get('USER')} | machine: {get_machine_name(machine)} | pid: {str(os.getpid())} | started at: {str(datetime.datetime.now())}\n"
        with open(constants.LOCK_FILE, "w") as f:
            f.write(lockstring)
        if machine < 2 and ssh_config.config != "NoSSH":
            ssh_config.config.ssh.run(
                'echo "' + lockstring + '" > ' + constants.LOCK_FILE
            )


def get_subfile(machine: Machine) -> str:
    # for now, we require that the file am.sub exists in the home directory for any user
    return "am.sub"
    # """Gets the name of the currect subfile based on the machine, or none if machine is not valid
    # Args:
    #  machine: The machine to get the subfile for,
    # Returns:
    #  str: The correct subfile for the machine
    #  If the machine is not a valid machine returns INVALID"""
    # return {
    #    Machine.FRI_ODEN: "fri.sub",
    #    Machine.HALIFAX_ODEN: "halifax.sub",
    #    Machine.STAMPEDE2_TACC: "knl.mpi.slurm",
    #    Machine.FRONTERRA_TACC: "clx.mpi.slurm",
    #    Machine.LS6_TACC: "milan.mpi.slurm",
    # }.get(machine, "INVALID")


def scp_put_dir(local: str, remote: str, ssh_config: SSHConfig) -> None:
    """Puts files inside the local directory to the remote directory

    Args:
      remote (str): the directory on the remote machine to transfer files to
      local (str): the directory on the local machine to transfer files from
    Returns:
      None
    """
    cwd = os.getcwd()
    os.chdir(local)
    for f in (
        subprocess.run(["find", ".", "-type", "f"], capture_output=True)
        .stdout.decode("utf-8")
        .split("\n")
    ):
        if len(f) < 1:
            continue
        dirname = os.path.dirname(remote + f[1:])
        ssh_config.ssh.run("mkdir -p " + dirname)  # type: ignore
        ssh_config.scp.put(local + f[1:], dirname)  # type: ignore
    os.chdir(cwd)


def automagic_exit(machine: Machine, ssh_config: SSHConfig) -> NoReturn:
    """Removes the lockfile and closes ssh if connected via SSH"""
    subprocess.call(["rm", constants.LOCK_FILE])
    if machine < 2 and ssh_config.config != "NoSSH":
        ssh_config.ssh.run("rm " + constants.LOCK_FILE)  # type: ignore
        ssh_config.ssh.close()  # type: ignore
    exit()


def is_oden(machine: Machine) -> bool:
    """Returns if the machine is owned by the oden institute

    In short this returns if the machine is in the set of
      FRI_ODEN (fri.oden.utexas.edu),
      HALIFAX_ODEN (halifax.oden.utexas.edu)
    """
    return machine in {Machine.FRI_ODEN, Machine.HALIFAX_ODEN}


def is_tacc(machine: Machine) -> bool:
    """Returns if the machine is in TACC

    In short this returns if the machine is in the set of
      STAMPEDE2_TACC (stempede2.tacc.utexas.edu)
      FRONTERRA_TACC (frontera.tacc.utexas.edu)
      LS6_TACC (ls6.tacc.utexas.edu)
    """
    return machine in {Machine.STAMPEDE2_TACC, Machine.FRONTERRA_TACC, Machine.LS6_TACC}
