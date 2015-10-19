# copyright 2015 CEA, all rights reserved.
# contact http://brainomics.cea.fr/ -- mailto:localizer94@cea.fr

"""cubicweb-localizer automatic tests


uncomment code below if you want to activate automatic test for your cube:

.. sourcecode:: python

    from cubicweb.devtools.testlib import AutomaticWebTest

    class AutomaticWebTest(AutomaticWebTest):
        '''provides `to_test_etypes` and/or `list_startup_views` implementation
        to limit test scope
        '''

        def to_test_etypes(self):
            '''only test views for entities of the returned types'''
            return set(('My', 'Cube', 'Entity', 'Types'))

        def list_startup_views(self):
            '''only test startup views of the returned identifiers'''
            return ('some', 'startup', 'views')
"""

from cubicweb.devtools import testlib

class DefaultTC(testlib.CubicWebTC):
    def test_something(self):
        self.skipTest('this cube has no test')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
