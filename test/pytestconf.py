# copyright 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
"""

"""
import os
import sys

from logilab.common.pytest import PyTester

def getlogin():
    """avoid usinng os.getlogin() because of strange tty / stdin problems
    (man 3 getlogin)
    Another solution would be to use $LOGNAME, $USER or $USERNAME
    """
    if sys.platform == 'win32':
        return os.environ.get('USERNAME') or 'cubicweb'
    import pwd
    return pwd.getpwuid(os.getuid())[0]


def update_parser(parser):
    login = getlogin()
    parser.add_option('-r', '--rebuild-database', dest='rebuild_db',
                      default=False, action="store_true",
                      help="remove tmpdb and rebuilds the test database")
    parser.add_option('-u', '--dbuser', dest='dbuser', action='store',
                      default=login, help="database user")
    parser.add_option('-w', '--dbpassword', dest='dbpassword', action='store',
                      default=login, help="database user's password")
    parser.add_option('-n', '--dbname', dest='dbname', action='store',
                      default=None, help="database name")
    parser.add_option('--euser', dest='euser', action='store',
                      default=login, help="euser name")
    parser.add_option('--epassword', dest='epassword', action='store',
                      default=login, help="euser's password' name")
    return parser


class CustomPyTester(PyTester):
    def __init__(self, cvg, options):
        super(CustomPyTester, self).__init__(cvg, options)
        if options.rebuild_db:
            os.unlink('tmpdb')
            os.unlink('tmpdb-template')
