# This file is part account_search_with_dot module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import re

from sql import Literal
from sql.operators import BinaryOperator, Like

from trytond.const import OPERATORS
from trytond.backend import name as backend_name
from trytond.transaction import Transaction
from trytond.pool import PoolMeta


class Regexp(BinaryOperator):
    __slots__ = ()
    _operator = 'REGEXP'


class PostgresqlRegexp(BinaryOperator):
    __slots__ = ()
    _operator = '~'


def regexp_function():
    db_type = backend_name
    if db_type == 'postgresql':
        return PostgresqlRegexp
    elif db_type == 'mysql':
        return Regexp
    return None


class CodeWithDotMixin(metaclass=PoolMeta):
    _dot_fields = ['code']

    @classmethod
    def get_ids(cls, q):
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
        return ids

    @classmethod
    def get_clause(cls, clause):
        clause = clause
        q = clause[2].replace('%', '').replace('*', '\*')
        if '.' in q:
            ids = cls.get_ids(q)
            if clause[1].startswith('not'):
                return ('id', 'not in', ids)
            else:
                return ('id', 'in', ids)

    @classmethod
    def search_domain(cls, domain, active_test=True, tables=None):
        '''
        Improves the search of accounts using a dot to fill the zeroes (like
        43.27 to search account 43000027)
        '''
        def is_leaf(expression):
            return (isinstance(expression, (list, tuple))
                and len(expression) > 2
                and isinstance(expression[1], str)
                and expression[1] in OPERATORS)  # TODO remove OPERATORS test

        def convert_domain(domain):
            'Replace missing product field by the MoveLine one'
            if is_leaf(domain):
                if domain[0] in 'code' and 'like' in domain[1] and domain[2]:
                    clause = cls.get_clause(domain)
                    if clause:
                        return clause
                return domain
            elif domain in ['OR', 'AND']:
                return domain
            else:
                return [convert_domain(d) for d in domain]
        return super().search_domain(convert_domain(domain),
            active_test=active_test, tables=tables)

    @classmethod
    def get_dot_extra_where(cls, table):
        return Literal(True)


class Account(CodeWithDotMixin):
    __name__ = 'account.account'

    @classmethod
    def get_dot_extra_where(cls, table):
        return (table.type != None)

    @classmethod
    def search_rec_name(cls, name, clause):
        '''
        Improves the search_rec_name allowing the use of a dot to fill the
        zeroes (like 43.27 to search account 43000027)
        '''
        res = super().search_rec_name(name, clause)
        if 'like' in clause[1]:
            new_clause = cls.get_clause(clause)
            if new_clause:
                if 'not' in new_clause[1]:
                    return ['AND', [new_clause], res]
                else:
                    return ['OR', [new_clause], res]
        return res
