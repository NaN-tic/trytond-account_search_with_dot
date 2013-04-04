#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import sys, os
DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction


class AccountSearchWithDotTestCase(unittest.TestCase):
    '''
    Test Account module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_search_with_dot')
        self.account_template = POOL.get('account.account.template')
        self.account = POOL.get('account.account')
        self.type = POOL.get('account.account.type')
        self.company = POOL.get('company.company')
        self.user = POOL.get('res.user')

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('account')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()

    def test0010account_chart(self):
        'Test creation of minimal chart of accounts'
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT) as transaction:
            account_template, = self.account_template.search([
                    ('parent', '=', None),
                    ])
            company, = self.company.search([('name', '=', 'B2CK')])
            self.user.write([self.user(USER)], {
                    'main_company': company.id,
                    'company': company.id,
                    })
            CONTEXT.update(self.user.get_preferences(context_only=True))

            session_id, _, _ = self.account_create_chart.create()
            create_chart = self.account_create_chart(session_id)
            create_chart.account.account_template = account_template
            create_chart.account.company = company
            create_chart.transition_create_account()
            receivable, = self.account.search([
                    ('kind', '=', 'receivable'),
                    ('company', '=', company.id),
                    ])
            payable, = self.account.search([
                    ('kind', '=', 'payable'),
                    ('company', '=', company.id),
                    ])
            create_chart.properties.company = company
            create_chart.properties.account_receivable = receivable
            create_chart.properties.account_payable = payable
            create_chart.transition_create_properties()
            transaction.cursor.commit()

def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.company.tests import test_company
    for test in test_company.suite():
        if test not in suite:
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountSearchWithDotTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
