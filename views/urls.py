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

"""cubicweb-brainomics views/forms/actions/components for web ui"""

from cubicweb.web.views.urlrewrite import SimpleReqRewriter, rgx


class LocalizerReqRewriter(SimpleReqRewriter):
    rules = [
        (rgx('/brainomics'),
         dict(rql=r'Any X WHERE X is Card, X title "brainomics"')),
        (rgx('/localizer'),
         dict(rql=r'Any X WHERE X is Card, X title "localizer"')),
        (rgx('/license'),
         dict(rql=r'Any X WHERE X is Card, X title "license"')),
        (rgx('/legal'),
         dict(rql=r'Any X WHERE X is Card, X title "legal"')),
        (rgx('/dataset'),
         dict(rql=r'Any X WHERE X is Card, X title "dataset"')),
        ]
