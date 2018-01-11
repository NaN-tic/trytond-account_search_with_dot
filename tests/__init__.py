# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
try:
    from trytond.modules.account_search_with_dot.tests.test_account_search_with_dot import suite
except ImportError:
    from .test_account_search_with_dot import suite

__all__ = ['suite']
