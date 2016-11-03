# This file is part account_search_with_dot module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import re

from sql import Literal
from sql.operators import BinaryOperator, Like

from trytond.backend import name as backend_name
from trytond.transaction import Transaction
from trytond.pool import PoolMeta

__all__ = ['Account', 'GeneralLedgerAccount']


class Regexp(BinaryOperator):
    __slots__ = ()
    _operator = 'REGEXP'


class PostgresqlRegexp(BinaryOperator):
    __slots__ = ()
    _operator = '~'


def regexp_function():
    db_type = backend_name()
    if db_type == 'postgresql':
        return PostgresqlRegexp
    elif db_type == 'mysql':
        return Regexp
    return None


class CodeWithDotMixin:
    __metaclass__ = PoolMeta
    _dot_fields = ['code']

    @classmethod
    def search(cls, args, offset=0, limit=None, order=None, count=False,
            query=False):
        """Improves the search of accounts using a dot to
        fill the zeroes (like 43.27 to search account
        43000027)
        """
        args = args[:]
        pos = 0
        while pos < len(args):
            if not args[pos]:
                pos += 1
                continue
            if (args[pos][0] in ('code', 'rec_name')
                    and args[pos][1] in ('like', 'ilike',
                    'not like', 'not ilike') and args[pos][2]):
                q = args[pos][2].replace('%', '')
                if '.' in q:
                    q = q.partition('.')
                    regexp = regexp_function()
                    table = cls.__table__()
                    where = cls.get_dot_extra_where(table)
                    if regexp:
                        expression = '^%s0+%s$' % (q[0], q[2])
                        ids = table.select(table.id, where=(where &
                                regexp(table.code, expression)))
                    else:
                        cursor = Transaction().connection.cursor()
                        cursor.execute(*table.select(table.id,
                                table.code, where=(where &
                                    Like(table.code, q[0] + '%' + q[2]))))
                        pattern = '^%s0+%s$' % (q[0], q[2])
                        ids = []
                        for record in cursor.fetchall():
                            if re.search(pattern, record[1]):
                                ids.append(record[0])
                    if args[pos][1].startswith('not'):
                        args[pos] = ('id', 'not in', ids)
                    else:
                        args[pos] = ('id', 'in', ids)
            pos += 1
        return super(CodeWithDotMixin, cls).search(args, offset=offset,
            limit=limit, order=order, count=count, query=query)

    @classmethod
    def get_dot_extra_where(cls, table):
        return Literal(True)


class Account(CodeWithDotMixin):
    __name__ = 'account.account'

    @classmethod
    def get_dot_extra_where(cls, table):
        return (table.kind != 'view')


class GeneralLedgerAccount(CodeWithDotMixin):
    __name__ = 'account.general_ledger.account'
