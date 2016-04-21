"""
Module that implements a simple wrapper for subprocess.check_output function

@author: Mikhail Dyakonov
@contact: mikhail.dyakonov@opensoftdev.com
@organization: Opensoft
"""

import subprocess
import logging
import sys

def execute_command(popenargs, cwd = None, timeout = None, silent = False) -> str:
    """
    Executes system command, returns output of the command and logs iy id log_level == logging.NOTSET
    If command fails, logs it output and raises exception

    :param popenargs: command to execute (see subprocess.check_output)
    :param timeout: command execution timeout in seconds
    :param cwd: command working directory if != None
    :param silent: if True, the function will not log the command output
    :return: command output (cout and cerr streams)
    """
    # timeout argument is supported in Python 3.4 and higher
    if sys.version_info < (3, 4):
        output = __execute_command_3_2(popenargs, cwd = cwd)
    else:
        output = __execute_command_3_4(popenargs, cwd = cwd, timeout = timeout)

    logging.info("CMD OK: %s (WITH CWD=%s)", ' '.join(popenargs), cwd)
    if not silent:
        for ln in output.split("\n"):
            logging.info("    %s", ln)

    return output


def __execute_command_3_2(popenargs, cwd) -> str:
    #execute_command function for python 3.2
    try:
        # timeout argument is supported in Python 3.4 and higher
        raw = subprocess.check_output(popenargs, cwd = cwd, stderr=subprocess.STDOUT)
        output = raw.decode(sys.stdout.encoding)
    except subprocess.CalledProcessError as e:
        logging.error("CMD FAILED: %s (WITH CWD=%s)", e.cmd, cwd)
        for ln in e.output.decode(sys.stdout.encoding).split("\n"):
            logging.error("    %s", ln)
        raise e
    except Exception as e:
        logging.error("CMD FAILED: %s (WITH CWD=%s)", e.cmd, cwd)
        logging.error("    %s", e)
        raise e

    return output

def __execute_command_3_4(popenargs, cwd, timeout) -> str:
    # execute_command function that works with python 3.4 and higher
    try:
        # timeout argument is supported in Python 3.4 and higher
        raw = subprocess.check_output(popenargs, cwd = cwd, timeout = timeout, stderr=subprocess.STDOUT)
        output = raw.decode(sys.stdout.encoding)
    except subprocess.TimeoutExpired as e:
        logging.error("TIMEOUT=%d EXPIRED FOR CMD=%s (WITH CWD=%s)", timeout, e.cmd, cwd)
        for ln in e.output.decode(sys.stdout.encoding).split("\n"):
            logging.error("    %s", ln)
        raise e
    except subprocess.CalledProcessError as e:
        logging.error("CMD FAILED: %s (WITH CWD=%s)", e.cmd, cwd)
        for ln in e.output.decode(sys.stdout.encoding).split("\n"):
            logging.error("    %s", ln)
        raise e
    except Exception as e:
        logging.error("CMD FAILED: %s (WITH CWD=%s)", e.cmd, cwd)
        logging.error("    %s", e)
        raise e

    return output

