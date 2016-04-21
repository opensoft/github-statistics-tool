#!/usr/bin/env python3

import sys
import os
import os.path
import datetime
import csv
import logging
import pprint
from CommandExecutor import execute_command


def write_combined_log(csvwriter, organisation, root, notlist) -> int:
    commits = 0
    logging.info("Get logs for: %s" % root)
    subfolders = [o for o in os.listdir(root) if os.path.isdir(os.path.join(root, o))]
    if ".git" not in subfolders:
        for fld in subfolders:
            commits += write_combined_log(csvwriter, organisation, os.path.join(root, fld), notlist)
    else:
        gitlog = execute_command(["git", "log", "--all", "--format=%cn,%ce,%ai"], cwd=root, silent=True, timeout=10).split("\n")
        rname = root[notlist:].replace("%20", " ")
        print("Repo: ", rname, end="")

        combined = dict()

        for commit in gitlog:
            spl = commit.split(",")
            if len(spl) != 3:
                continue
            (name, email, date) = spl
            commits += 1

            dt = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m")
            if dt not in combined:
                combined[dt] = dict()

            if email not in combined[dt]:
                combined[dt][email] = {"author": name, "commits": 1}
            else:
                combined[dt][email]["commits"] += 1

        for month, month_rec in combined.items():
            for email, rec in month_rec.items():
                csvwriter.writerow([organisation,
                                    rname,
                                    month,
                                    email,
                                    rec["author"],
                                    rec["commits"]]
                                   )

        print(" => ", commits)

    return commits


def main():
    if len(sys.argv) == 1:
        print("Usage:\n   ./tfs-logs.py <root_folder> <csv-filename>")
        return

    logging.basicConfig(format='%(asctime)s %(levelname)s> %(message)010s', level=logging.WARNING)

    dir_start = sys.argv[1]
    ofname = sys.argv[2]

    if os.path.isfile(ofname):
        print("FATAL: File '%s' already exists" % ofname)
        return

    with open(ofname, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(["Company", "Project", "Month", "Email", "Author", "Commits"])
        count = write_combined_log(csvwriter, "opensoft", dir_start, len(dir_start))
        print(count, " commits saved")


if __name__ == "__main__":
    if sys.version_info < (3, 2):
        print("FATAL: This software requires Python 3.2 or higher")
        sys.exit(1)
    else:
        main()
