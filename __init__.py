# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import account


def register():
    Pool.register(
        account.Account,
        account.GeneralLedgerAccount,
        module='account_search_with_dot', type_='model')
