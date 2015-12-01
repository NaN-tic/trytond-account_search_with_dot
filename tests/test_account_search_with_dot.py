# This file is part of the account_search_with_dot module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountSearchWithDotTestCase(ModuleTestCase):
    'Test Account Search With Dot module'
    module = 'account_search_with_dot'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountSearchWithDotTestCase))
    return suite