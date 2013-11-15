# -*- coding: utf-8 -*-
# copyright 2013 CEA (Saclay, FRANCE), all rights reserved.
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://brainomics.cea.fr -- mailto:localizer94@cea.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import os.path as osp

HERE = osp.abspath(osp.dirname(__file__))

###############################################################################
### CARDS AND IMAGES DEFINITIONS ##############################################
###############################################################################
HTMLS = {u'index': open(osp.join(HERE, 'static_pages/index.html')).read().decode('utf8'),
         u'brainomics': open(osp.join(HERE, 'static_pages/brainomics.html')).read().decode('utf8'),
         u'localizer': open(osp.join(HERE, 'static_pages/localizer.html')).read().decode('utf8'),
         u'license': open(osp.join(HERE, 'static_pages/license.html')).read().decode('utf8'),
         u'legal': open(osp.join(HERE, 'static_pages/legal.html')).read().decode('utf8'),
         u'dataset': open(osp.join(HERE, 'static_pages/dataset.html')).read().decode('utf8')}


###############################################################################
### CREATE OR UPDATE FUNCTION #################################################
###############################################################################
def create_or_update_static_cards(session):
    """ Create or update the cards for static pages
    """
    for _id, html in HTMLS.iteritems():
        rset = session.execute('Any X WHERE X is Card, X title %(s)s', {'s': _id})
        if rset:
            session.execute('SET X content %(c)s WHERE X is Card, X title %(s)s',
                            {'c': html, 's': _id})
        else:
            session.create_entity('Card', content_format=u'text/html', title=_id, content=html)


###############################################################################
### MAIN ######################################################################
###############################################################################
if __name__ == '__main__':
    create_or_update_static_cards(session)
