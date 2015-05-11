# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .account import *


def register():
    Pool.register(
        Account,
        module='account_search_with_dot', type_='model')
