# This file is part of the account_search_with_dot module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import doctest
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction


class AccountSearchWithDotTestCase(ModuleTestCase):
    'Test Account Search With Dot module'
    module = 'account_search_with_dot'

    def setUp(self):
        super(AccountSearchWithDotTestCase, self).setUp()
        self.account = POOL.get('account.account')

    def test0010search_with_dot(self):
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            receivable, = self.account.search([
                    ('kind', '=', 'receivable'),
                    ])
            receivable.code = '43000001'
            receivable.save()
            payable, = self.account.search([
                    ('kind', '=', 'payable'),
                    ])
            payable.code = '41000001'
            payable.save()

            for field in ('code', 'rec_name'):
                account, = self.account.search([(field, 'ilike', '43.1')])
                self.assertEqual(account.code, u'43000001')
                account, = self.account.search([(field, 'ilike', '41.1')])
                self.assertEqual(account.code, u'41000001')


def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.account.tests import test_account
    for test in test_account.suite():
        if test not in suite and not isinstance(test, doctest.DocTestCase):
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountSearchWithDotTestCase))
    return suite
