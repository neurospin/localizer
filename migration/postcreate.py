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

"""cubicweb-localizer postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

set_property('ui.site-title', 'Brainomics/Localizer')

from cubes.localizer.migration.cards import create_or_update_static_cards
create_or_update_static_cards(session)
