# This file is part of the account_search_with_dot module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
from trytond.pool import Pool
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction

from trytond.modules.company.tests import create_company, set_company
from trytond.modules.account.tests import create_chart


class AccountSearchWithDotTestCase(ModuleTestCase):
    'Test Account Search With Dot module'
    module = 'account_search_with_dot'

    @with_transaction()
    def test0010search_with_dot(self):
        pool = Pool()
        Account = pool.get('account.account')
        company = create_company()
        with set_company(company):
            create_chart(company, tax=True)
            receivable, = Account.search([
                    ('kind', '=', 'receivable'),
                    ])
            receivable.code = '43000001'
            receivable.save()
            payable, = Account.search([
                    ('kind', '=', 'payable'),
                    ])
            payable.code = '41000001'
            payable.save()

            for field in ('code', 'rec_name'):
                account, = Account.search([(field, 'ilike', '43.1')])
                self.assertEqual(account.code, u'43000001')
                account, = Account.search([(field, 'ilike', '41.1')])
                self.assertEqual(account.code, u'41000001')


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountSearchWithDotTestCase))
    return suite
