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
from typing import List, Optional, Union
from dataclasses import dataclass


@dataclass
class SubTransaction(object):
    id: str
    transaction_id: str
    amount: int
    memo: str
    payee_id: str
    payee_name: str
    category_id: str
    category_name: str
    transfer_account_id: str
    transfer_transaction_id: str
    deleted: bool


@dataclass
class Transaction(object):
    id: str
    date: str
    amount: int
    memo: str
    cleared: str
    approved: bool
    flag_color: str
    account_id: str
    payee_id: str
    category_id: str
    transfer_account_id: str
    transfer_transaction_id: str
    matched_transaction_id: str
    import_id: str
    deleted: bool
    account_name: str
    payee_name: str
    category_name: str
    flag_name: str = None
    subtransactions: Optional[List[dict]] = None
    import_payee_name_original: Optional[str] = None
    import_payee_name: Optional[str] = None
    debt_transaction_type: Optional[str] = None
    transaction_id: Optional[str] = None
    type: Optional[str] = None
    parent_transaction_id: Optional[str] = None
    server_knowledge: Optional[int] = None

    def __repr__(self):
        return f"Transaction({self.account_name}, {self.payee_name})"


@dataclass
class Account(object):
    id: str
    name: str
    type: str
    on_budget: bool
    closed: bool
    note: str
    balance: int
    cleared_balance: int
    uncleared_balance: int
    transfer_payee_id: str
    direct_import_linked: bool
    direct_import_in_error: bool
    last_reconciled_at: str
    debt_original_balance: int
    debt_interest_rates: dict
    debt_minimum_payments: dict
    debt_escrow_amounts: dict
    deleted: bool
    server_knowledge: Optional[int] = None
    transactions: List[Transaction] = None

    def __repr__(self):
        return f"Account({self.name})"


@dataclass
class Category(object):
    id: str
    category_group_id: str
    category_group_name: str
    name: str
    hidden: bool
    deleted: bool
    original_category_group_id: str
    note: str
    budgeted: int
    activity: int
    balance: int
    goal_type: str
    goal_day: int
    goal_cadence: int
    goal_cadence_frequency: int
    goal_creation_month: str
    goal_target: int
    goal_target_month: str
    goal_percentage_complete: int
    goal_months_to_budget: int
    goal_under_funded: int
    goal_overall_funded: int
    goal_overall_left: int
    goal_needs_whole_amount: bool
    deleted: bool
    server_knowledge: Optional[int] = None
    transactions: Optional[List[Transaction]] = None

    def __repr__(self):
        return f"Category({self.name})"


@dataclass
class User(object):
    id: str


@dataclass
class Budget(object):
    id: str
    name: str
    last_modified_on: str
    first_month: str
    last_month: str
    date_format: dict
    currency_format: dict
    accounts: Optional[List[Account]] = None
    categories: Union[List[Category], Category, None] = None
    user: Optional[User] = None

    def __repr__(self):
        return f"Budget({self.name}, {self.last_modified_on})"
