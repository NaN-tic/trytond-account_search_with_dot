
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction

from trytond.modules.company.tests import (CompanyTestMixin, create_company,
    set_company)
from trytond.modules.account.tests import create_chart


class AccountSearchWithDotTestCase(CompanyTestMixin, ModuleTestCase):
    'Test AccountSearchWithDot module'
    module = 'account_search_with_dot'

    @with_transaction()
    def test0010search_with_dot(self):
        pool = Pool()
        Account = pool.get('account.account')

        company = create_company()
        with set_company(company):
            create_chart(company, tax=True)
            receivable, = Account.search([
                    ('type.receivable', '=', True),
                    ])
            receivable.code = '43000001'
            receivable.save()
            payable, = Account.search([
                    ('type.payable', '=', True),
                    ])
            payable.code = '41000001'
            payable.save()

            for Model, field in [
                    (Account, 'code'),
                    (Account, 'rec_name'),
                    ]:
                account, = Model.search([(field, 'ilike', '43.1')])
                self.assertEqual(account.code, '43000001')
                account, = Model.search([(field, 'ilike', '41.1')])
                self.assertEqual(account.code, '41000001')


del ModuleTestCase
