"""
Module for listing all avaliable repos on github to check what are missed for mirroring

@author: Mikhail Dyakonov
@contact: mikhail.dyakonov@opensoftdev.com
@organization: Opensoft
"""

# import logging
# from requests.auth import HTTPDigestAuth

import requests
import json
import logging
import datetime

from Config import Config
# from CommandExecutor import execute_command

MAX_NUMBER_OF_PAGES = 500

class GithubCartographer(object):
    """
    A class that enumerates avaliable repositories on github
    """

    def __init__(self, conf: Config, organisation: str):
        self._api = conf["github"]["api"]
        self._organisation = organisation
        self._username = conf["github"]["username"]
        self._token = conf["github"]["api_token"]

    def list_all(self):
        """
        Enumerates all github repositories for the organization
        :return: list[str]
        """
        rlist = list()
        url = self._api + "orgs/" + self._organisation + "/repos"

        for page in range(1, MAX_NUMBER_OF_PAGES): # github returns 30 items per page
            params = {"sort": "updated", "direction":"asc", "type": "sources", "page":page}
            r = requests.get(url, auth=(self._username, self._token), params=params)
            if r.status_code != 200:
                raise Exception("Can't access %s: %s" % (url, repr(r)))
            js = json.loads(r.text)
            if js and len(js)>0:
                for repo in js:
                    #if not repo["fork"]:
                    rlist.append(self.__extract_repo_data(repo))
            else:
                break
        return sorted(rlist, key=lambda repo: datetime.datetime.strptime(repo["updated"], "%Y-%m-%dT%H:%M:%SZ"))

    def get_repo_by_name(self, conf: Config, repository_name: str) -> dict:
        """
        Returns github repo description by Name, return None if repo doesn't exist
        :param conf: configuration object
        :param repository_name: repository name (without slashes and trailing '.git')
        :return:
        """
        url = self._api + "repos/" + self._organisation + "/" + repository_name
        print(url)
        r = requests.get(url, auth=(self._username, self._token))
        if r.status_code == 404:
            logging.error("Repository '%s' was not found for orgsnisation '%s' at github" % (repository_name, self._organisation))
            return None
        if r.status_code != 200:
            raise Exception("Can't access %s: %s" % (url, repr(r)))
        js = json.loads(r.text)
        if js and len(js)>0:
            return self.__extract_repo_data(js)
        else:
            return None

    def __extract_repo_data(self, repo):
        return {
            "name": repo["name"],
            "git_ssh": repo["ssh_url"],
            "git_https": repo["clone_url"],
            "full_name": repo["full_name"],
            "description": repo["description"],
            "created": repo["created_at"],
            "updated": repo["pushed_at"],
            "language": repo["language"],
            "private": repo["private"],
            "owner": repo["owner"]["login"],
            "fork": repo["fork"]
        }

    @property
    def username(self):
        return self._username

    @property
    def organisation(self):
        return self._organisation


def do_test():
    from pprint import pprint
    conf = Config("config/config.json")
    gcf = GithubCartographer(conf)
    repos = gcf.list_all()
    pprint(repos)
    print("\n\nlen = %d" % len(repos))

    print("Get data for repo ")
    print(gcf.get_repo_by_name(conf, "git-cloner"))

if __name__ == "__main__":
    do_test()