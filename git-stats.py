#!/usr/bin/env python3
"""
Utility to get statistics for all organisation repositories

@author: Mikhail Dyakonov
@contact: mikhail.dyakonov@opensoftdev.com
@organization: Opensoft
"""

import sys
import logging
import os.path
import csv
import datetime

from Config import Config
from GithubCartographer import GithubCartographer
from RepoGitlogReader import RepoGitlogReader

CONF_FILE_NAME = "config" + os.path.sep + "config.json"

def get_help() -> str:
    return (
        "Get commit statistics for the organisation in CSV format\n"\
        "Usage:\n"\
        "    ./git-stats <organisation> -csv <csv-filename> [-limit <number>]\n"\
        "Examples:\n"\
        "  Save all commits for the opensoft organisation to the file\n"\
        "    ./git-stats opensoft -csv commiters.csv\n"\
        "  Save all commits for the first 5 repos in opensoft to csv file (this is useful for testing)\n"\
        "    ./git-stats opensoft -csv commiters.csv -limit 5\n"
        )


def write_git_log(conf: Config, csvwriter, organisation, skip = None, limit = None) -> int:
    cartographer = GithubCartographer(conf, organisation)
    repos = cartographer.list_all()[skip:limit]

    rcount = len(repos)
    print("Total number of repositories found: %i" % rcount)

    gitlog_reader = RepoGitlogReader(conf)

    processed = 1
    ccount = 0
    for r in repos:
        print("[%i/%i] %s " % (processed, rcount, r["name"]), end="", flush=True)
        gitlog = gitlog_reader.get_repo_commits(organisation, r["name"])
        commits = len(gitlog)
        print(" %i commits" % commits)
        ccount += commits

        for c in gitlog:
            dt = datetime.datetime.strptime(c["author"]["date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
            csvwriter.writerow([organisation,
                                r["name"],
                                c["author"]["name"],
                                c["author"]["email"],
                                dt]
                               )

        processed += 1

    return ccount


def main() -> None:
    logging.basicConfig(format='%(asctime)s %(levelname)s> %(message)010s', level=logging.WARN)

    if len(sys.argv) < 4 or sys.argv[2] != "-csv":
        print(get_help())
        return

    organisation = sys.argv[1]
    ofname = sys.argv[3]

    limit = None
    # skip some number of repositories from the beginning of the list, for dev bugfixing only
    skip = 0
    if len(sys.argv) == 6:
        if sys.argv[4] == "-limit":
            limit = int(sys.argv[5])
        else:
            print("FATAL: Unknown parameter")
            print(get_help())
            return


    # read config
    config = Config(CONF_FILE_NAME)

    # Setting up a new log level
    logging.root.setLevel(config.get_log_level())

    if os.path.isfile(ofname):
        print("FATAL: File '%s' already exists" % ofname)
        return

    with open(ofname, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(["Company", "Project", "Author", "Email", "Date"])
        count = write_git_log(config, csvwriter, organisation, skip = skip, limit = limit)
        print(count, " commits saved")


if __name__ == "__main__":
    if sys.version_info < (3, 2):
        print("FATAL: This software requires Python 3.2 or higher")
        sys.exit(1)
    else:
        main()
