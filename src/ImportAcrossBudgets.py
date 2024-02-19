# -*- coding: utf-8 -*-
"""
Script to migrate user input transactions from one budget to another.
"""

# metadata
__author__ = "Ty Keith"
__version__ = "0.0.1"
__maintainer__ = __author__
__email__ = "itisme@tykeith.dev"
__status__ = "PROD"
__deprecated__ = False
__ROOT__ = r"/Users/ty/Documents/Python/YNAB/src"

# imports
import datetime
import sys
import os

sys.path.append(__ROOT__)
os. chdir(__ROOT__)

# custom party imports
from src.Classes.rest_calls import RESTRequests
from src.Classes.YNABObjects import Budget, Transaction, Account, Category
from typing import List, Optional


class ImportAcrossBudgets:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self, to_budget_name: str, from_budget_name: str, to_budget_account: str, from_budget_category: str, since_date: str):
        # init variables
        self.__requests = RESTRequests()
        self.to_budget_name = to_budget_name
        self.to_budget_account = to_budget_account
        self.from_budget_name = from_budget_name
        self.from_budget_category = from_budget_category
        self.since_date = since_date

        # derived variables
        self.to_budget, self.from_budget = self.construct_budgets()

        # del variables that cause clutter for debugging
        # TODO: refactor later to pass these vars instead of making them self (global) vars
        del self.to_budget_name, self.from_budget_name, self.to_budget_account, self.from_budget_category

    def execute(self) -> None:
        """
        Move transactions from one budget to another as input by the user in the construction of the script object.
        :return: None
        """

        # get transactions to add
        transactions_to_add = self.get_transactions_to_add()
        transactions_to_add_list = []

        # if transactions are identified add them into the to_budget
        if len(transactions_to_add) > 0:
            for transaction in transactions_to_add:
                transactions_to_add_list.append({
                    "account_id": self.to_budget.accounts.id,
                    "date": transaction.date,
                    "amount": transaction.amount,
                    "payee_name": transaction.payee_name,
                    "memo": transaction.memo,
                    "cleared": transaction.cleared,
                    "approved": transaction.approved,
                    "flag_color": transaction.flag_color
                })

            # format transactions and pass to the request to be added via the api
            trans_dict = dict(transactions=transactions_to_add_list)
            response = self.__requests.make_request(
                method="POST",
                url=f"{self.__requests.api_url()}{self.__requests.get_budget(budget_id=self.to_budget.id)}{self.__requests.get_transactions()}",
                _json=trans_dict
            )

            # print out the transactions that were added
            for item in response['data']['transactions']:
                print(f"Added {item['payee_name']} for Amount ${float(item['amount']/1000)} into {self.to_budget.name}-{item['account_name']}")
        # notify user nothing was added
        else:
            print(f"No transactions to be added to {self.to_budget.name} budget")

    def get_transactions_to_add(self) -> List[dict]:
        """
        This method compares to transactions in the to_budget account to the from budget category and returns a list of transactions to add
        :return: list of dictionaries to add
        """

        # init list to be returned
        transactions_to_add = []

        # create a list compare transactions to
        existing_to_trans = [f"{x.payee_name}::{x.amount}::{x.date}".lower() for x in self.to_budget.accounts.transactions]

        # do the comparison
        for from_trans in self.from_budget.categories.transactions:
            if f"{from_trans.payee_name}::{from_trans.amount}::{from_trans.date}".lower() not in existing_to_trans:
                transactions_to_add.append(from_trans)

        return transactions_to_add

    def construct_budgets(self) -> tuple:
        """
        Creates budget object to be used as the main object to compare
        :return:
        """

        # init vars
        to_budget = None
        from_budget = None

        # set to and from budgets
        budgets = self.__requests.make_request(
            method="GET",
            url=f"{self.__requests.api_url()}{self.__requests.get_budgets()}"
        )

        # compare budgets from input name to budgets from YNAB
        for budget in budgets['data']['budgets']:
            if budget['name'] == self.to_budget_name:
                to_budget = Budget(**budget)
                to_budget.accounts = self.construct_accounts(budget_id=to_budget.id)

            if budget['name'] == self.from_budget_name:
                from_budget = Budget(**budget)
                from_budget.categories = self.construct_categories(budget_id=from_budget.id)

        if to_budget is None or from_budget is None:
            return None, None
        else:
            return to_budget, from_budget

    def construct_categories(self, budget_id: str) -> Optional[Category]:
        """
        Constructs the categories objects to be added into the budget object
        :param budget_id: guuid of the budget
        :return: None type or constructed budget object
        """

        # make call to ynab api for categories within the budget
        categories = self.__requests.make_request(
            method="GET",
            url=f"{self.__requests.api_url()}"
                f"{self.__requests.get_budget(budget_id=budget_id)}"
                f"{self.__requests.get_categories()}"
        )

        # loop through the budgets categories and create the from_budget variables
        for category_group in categories['data']['category_groups']:
            if not category_group['hidden'] or category_group['deleted']:
                for category in category_group['categories']:
                    if category['name'] == self.from_budget_category:
                        c_obj = Category(**category)
                        c_obj.server_knowledge = categories['data']['server_knowledge']
                        c_obj.transactions = self.construct_transactions(budget_id=budget_id, category_id=c_obj.id)
                        return c_obj

    def construct_accounts(self, budget_id: str):
        """
        Constructs the accounts object to be added into the budget object
        :param budget_id:
        :return:
        """

        # make call to ynab api for accounts within the budget
        accounts = self.__requests.make_request(
            method="GET",
            url=f"{self.__requests.api_url()}"
                f"{self.__requests.get_budget(budget_id=budget_id)}"
                f"{self.__requests.get_accounts()}"
        )

        # loop through the budgets accounts and create the to_budget variables
        for account in accounts['data']['accounts']:
            if not account['deleted']:
                if account['name'] == self.to_budget_account:
                    a_obj = Account(**account)
                    a_obj.server_knowledge = accounts['data']['server_knowledge']
                    a_obj.transactions = self.construct_transactions(budget_id=budget_id, account_id=a_obj.id)
                    return a_obj

    def construct_transactions(self, budget_id: str, category_id: str = None, account_id: str = None):
        """
        This method constructs transactions from a category and budget id
        :param budget_id: uuid for the associated budget
        :param category_id: uuid for the associated category
        :param account_id:uuid for the associated account
        :return:
        """

        # init vars
        transaction_list = []
        transactions = []

        # build account and category transactions
        if category_id is not None:
            transactions = self.__requests.make_request(
                method="GET",
                url=f"{self.__requests.api_url()}"
                    f"{self.__requests.get_budget(budget_id=budget_id)}"
                    f"{self.__requests.get_category(category_id)}"
                    f"{self.__requests.get_transactions()}",
                params=dict(since_date=self.since_date)
            )
        elif account_id is not None:
            transactions = self.__requests.make_request(
                method="GET",
                url=f"{self.__requests.api_url()}"
                    f"{self.__requests.get_budget(budget_id=budget_id)}"
                    f"{self.__requests.get_account(account_id=account_id)}"
                    f"{self.__requests.get_transactions()}",
                params=dict(since_date=self.since_date)
            )

        # if transactions has a parent and no payee name then get the name from the parent
        for item in transactions['data']['transactions']:
            if item.get('payee_name') is None and item.get('parent_transaction_id') is not None:

                parent_trans = self.__requests.make_request(
                    method="GET",
                    url=f"{self.__requests.api_url()}"
                        f"{self.__requests.get_budget(budget_id=budget_id)}"
                        f"{self.__requests.get_transaction(transaction_id=item.get('parent_transaction_id'))}"
                )

                item['payee_name'] = parent_trans['data']['transaction']['payee_name']

            transaction_list.append(Transaction(**item))

        return transaction_list


if __name__ == "__main__":
    args = dict(
        to_budget_name="Tyhler",
        to_budget_account="Shared MasterCard",
        from_budget_name="131 Deer Run Close",
        from_budget_category="Ty Owes to Shared MC",
        since_date=f"{datetime.datetime.now().strftime('%Y-%m')}-01"
    )
    with ImportAcrossBudgets(**args) as script_tool:
        script_tool.execute()
