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
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            company, = self.company.search([('name', '=', 'B2CK')])
            user = self.user.search([('id', '=', USER)])
            self.user.write(user, {
                    'main_company': company,
                    'company': company,
                    })
            type_id = self.type.create([{
                    'name': 'Type',
                    'company': company,
                    }])[0]

            first_id = self.account.create([{
                    'code': '1000000',
                    'name': 'One',
                    'kind': 'payable',
                    'company': company,
                    'type': type_id,
                    }])[0]
            second_id = self.account.create([{
                    'code': '1000001',
                    'name': 'Two',
                    'kind': 'payable',
                    'company': company,
                    'type': type_id,
                    }])[0]
            result = self.account.search([('code','like','1.')])
            self.assertEqual(result, [first_id])
            result = self.account.search([('code','ilike','1.')])
            self.assertEqual(result, [first_id])
            result = self.account.search([('code','not like','1.')])
            self.assertEqual(result, [second_id])
            result = self.account.search([('code','not ilike','1.')])
            self.assertEqual(result, [second_id])
            result = self.account.search([('code','like','1.1')])
            self.assertEqual(result, [second_id])
            result = self.account.search([('code','ilike','1.1')])
            self.assertEqual(result, [second_id])
            result = self.account.search([('code','not like','1.1')])
            self.assertEqual(result, [first_id])
            result = self.account.search([('code','not ilike','1.1')])
            self.assertEqual(result, [first_id])

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
