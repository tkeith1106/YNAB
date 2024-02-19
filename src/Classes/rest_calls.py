# -*- coding: utf-8 -*-
"""
Short description:

Long Description:

Examples:

"""

# metadata
__author__ = "Ty Keith"
__version__ = "0.0.1"
__maintainer__ = __author__
__email__ = "itisme@tykeith.dev"
__status__ = "DEV"
__deprecated__ = False
__ROOT__ = r"/Users/ty/Documents/Python/YNAB.src"

# imports
import requests
from typing import Optional
from dataclasses import dataclass
import json

# custom party imports
import src.config as config


@dataclass
class RESTRequests(object):
    """

    """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self):

        # protected variables
        self.__method_list: list = ["GET", "POST"]
        self.__response_list: list = [400, 401, 403, 404, 409, 429, 500, 503]
        self._x_rate_limit: Optional[tuple] = None

        # self vars
        self.remaining_rest_calls: Optional[int] = self.__get_remaining_calls()

    def make_request(self, method: str, url: str, params: dict = None, _json: dict = None, headers: dict = None) -> dict:
        """
        This method is used to standardize the rest calls made to the YNAB API and give some information on the response,
         If needed.
        :param method: the type of request to make to the server
        :param url: the url to submit to the server
        :param params: a dictionary of request parameters to submit to the server
        :param headers: a dictionary of request headers to submit to the server
        :return:
        """

        if self._x_rate_limit is not None and self.remaining_rest_calls == 0:
            return dict(message="X-Limit hit no REST calls remaning. Please try again later.")

        # add some defaults into the params, if not already there
        if params is not None and params.get('f') is None:
            params['f'] = "json"
        elif params is None and method == 'GET':
            params = dict(f="json")

        # add some defaults into the headers, if not already there
        if headers is not None and headers.get('Authorization') is None:
            headers["Authorization"] = f"Bearer {config.API_TOKEN}"
        elif headers is None:
            headers = {"Authorization": f"Bearer {config.API_TOKEN}", "content-type": "application/json", "Referer": f"{self.api_url()}"}

        # make appropriate request based off method
        if method == 'GET':
            r = requests.get(url=url, params=params, headers=headers)
        elif method == 'POST':
            r = requests.post(url=url, params=params, data=json.dumps(_json).encode(), headers=headers)
        else:
            raise ValueError(
                f"User input method not supported: {method=}\t|\t Supported Methods [{', '.join(self.__method_list)}]")

        # deal with the response
        if r.status_code in [200, 201]:
            self._x_rate_limit = r.headers._store.get('x-rate-limit')
            self.__get_remaining_calls()

            return r.json()
        elif r.status_code in self.__response_list:
            raise ValueError(f"Bad Server Response [{r.status_code}]: {r.json()}")
        else:
            raise RuntimeError(f"There is an issue with the request response: {r.json()}")

    def __get_remaining_calls(self) -> Optional[int]:
        """
        This method returns how many rest calls are remaining
        :return: integer of the remaining rest calls or None type if unknown
        """

        if self._x_rate_limit is not None and isinstance(self._x_rate_limit, tuple):
            remaining_calls = int(self._x_rate_limit[1].split("/")[-1]) - int(self._x_rate_limit[1].split("/")[0])
            self.remaining_rest_calls = remaining_calls
            return remaining_calls
        else:
            return None

    @staticmethod
    def api_url():
        return r"https://api.ynab.com/v1"
    
    @staticmethod
    def get_budgets():
        return f"/budgets"

    @staticmethod
    def get_budget(budget_id):
        return f"/budgets/{budget_id}"

    @staticmethod
    def get_user_info():
        return "/user"
    
    @staticmethod
    def get_categories():
        return f"/categories"

    @staticmethod
    def get_category(category_id: str):
        return f"/categories/{category_id}"

    @staticmethod
    def get_category_by_month(month: str, category_id: str):
        return f"/months/{month}/categories/{category_id}"

    @staticmethod
    def get_account(account_id):
        return f"/accounts/{account_id}"

    @staticmethod
    def get_accounts():
        return f"/accounts"
    
    @staticmethod
    def get_transactions():
        return f"/transactions"

    @staticmethod
    def get_transaction(transaction_id: str):
        return f"/transactions/{transaction_id}"


if __name__ == "__main__":
    with RESTRequests() as script:
        response = script.make_request(method="GET", url=r"https://api.ynab.com/v1/budgets")
        print(f"{response=}")
        print(f"{script.__dict__}")