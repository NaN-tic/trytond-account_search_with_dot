#This file is part account_search_with_dot module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
import re
from trytond.transaction import Transaction
from trytond.pool import PoolMeta
from trytond.config import CONFIG

__all__ = ['Account']
__metaclass__ = PoolMeta

class Account:
    'Account'
    __name__ = 'account.account'

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
            if (args[pos][0] in ('code', 'rec_name') 
                    and args[pos][1] in ('like', 'ilike', 
                    'not like', 'not ilike') and args[pos][2]):
                cursor = Transaction().cursor
                query = args[pos][2].replace('%','')
                if '.' in query:
                    query = query.partition('.')
                    if CONFIG['db_type'] == 'postgresql':
                        regexp = '~'
                    elif CONFIG['db_type'] == 'mysql':
                        regexp = 'REGEXP'
                    else:
                        regexp = None
                    if regexp:
                        cursor.execute("SELECT id FROM " + cls._table + 
                            " WHERE kind <> 'view' AND "
                            "code " + regexp + 
                            " ('^' || %s || '0+' || %s || '$')",
                            (query[0], query[2]))
                        ids = [x[0] for x in cursor.fetchall()]
                    else:
                        cursor.execute("SELECT id, code FROM " + cls._table + 
                            " WHERE kind <> 'view' AND "
                            "code LIKE %s", (query[0] + '%' + query[2],))
                        pattern = '^%s0+%s$' % (query[0], query[2])
                        ids = []
                        for record in cursor.fetchall():
                            if re.search(pattern, record[1]):
                                ids.append(record[0])
                    if ids:
                        if args[pos][1].startswith('not'):
                            args[pos] = ('id', 'not in', ids)
                        else:
                            args[pos] = ('id', 'in', ids)
            pos += 1
        return super(Account, cls).search(args, offset=offset, limit=limit,
                order=order, count=count, query=query)
