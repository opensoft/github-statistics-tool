"""
Module for reading gitlog for the specifiet github repository

@author: Mikhail Dyakonov
@contact: mikhail.dyakonov@opensoftdev.com
@organization: Opensoft
"""

import requests
import json
import logging
import datetime

from Config import Config
# from CommandExecutor import execute_command

MAX_NUMBER_OF_PAGES = 1000

class RepoGitlogReader(object):
    """
    A class to get a list of all commits to the specified repository
    """

    def __init__(self, conf: Config):
        self._api = conf["github"]["api"]
        self._username = conf["github"]["username"]
        self._token = conf["github"]["api_token"]
        self._since = conf["timeframe"]["since"]
        self._until = conf["timeframe"]["until"]

    def get_repo_commits(self, owner, repo):
        gitlog = list()
        url = self._api + "repos/" + owner + "/" + repo + "/commits"

        for page in range(1, MAX_NUMBER_OF_PAGES):  # github returns 30 items per page1
            params = {"page": page}
            if page == MAX_NUMBER_OF_PAGES:
                logging.warning("Maximum page number of %i was hit for this repo", page)
            if self._since:
                params["since"] = self._since
            if self._until:
                params["until"] = self._until

            r = requests.get(url, auth=(self._username, self._token), params=params)
            if r.status_code == 409:
                logging.warning("Error 409 on getting commits for '%s' (empty repo ?), skipping" % repo)
                break
            if r.status_code != 200:
                raise Exception("Can't access %s: %s" % (url, repr(r)))
            js = json.loads(r.text)
            if js and len(js) > 0:
                for commit in js:
                    # if not repo["fork"]:
                    gitlog.append(self.__get_commit_data(commit))
            else:
                break
        return gitlog


    def __get_commit_data(self, commit):
        return {
            "sha":          commit["sha"],
            "message":      commit["commit"]["message"],
            "author":       commit["commit"]["author"]
        }

def do_test():
    from pprint import pprint
    conf = Config("config/config.json")
    gitlog = RepoGitlogReader(conf)
    commits = gitlog.get_repo_commits("opensoft", "JsiInject")
    pprint(commits)

if __name__ == "__main__":
    do_test()