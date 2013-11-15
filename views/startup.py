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

from cubicweb.predicates import is_instance, authenticated_user, anonymous_user, yes
from cubicweb.view import EntityView
from cubicweb.web.views.primary import PrimaryView
from cubicweb.web.action import Action
from cubes.brainomics.views.startup import BrainomicsIndexView
from cubes.brainomics.views.download import DataZipAbstractView
from cubes.brainomics.views.download import DataZipAuthenticatedView
from cubes.brainomics.views.download import DataZipAnonymousView
from cubes.brainomics.views.actions import BrainomicsAbstractDownloadAction, ScanZipFileBox
ZIP_DOWNLOADABLE = ('Scan',)

###############################################################################
### CARD VIEW #################################################################
###############################################################################
class LocalizerDataZipAbstractView(DataZipAbstractView):
    __select__ = EntityView.__select__ & is_instance(*ZIP_DOWNLOADABLE)


class LocalizerDataZipAuthenticatedView(DataZipAuthenticatedView):
    __select__ = LocalizerDataZipAbstractView.__select__ & authenticated_user()


class LocalizerDataZipAnonymousView(DataZipAnonymousView):
    __select__ = LocalizerDataZipAbstractView.__select__ & anonymous_user()


class LocalizerScanZipFileBox(ScanZipFileBox):
    __select__ = BrainomicsAbstractDownloadAction.__select__  & is_instance(*ZIP_DOWNLOADABLE)


class LocalizerIndexView(BrainomicsIndexView):

    def call(self, **kwargs):
        rset = self._cw.execute('Any X WHERE X is Card, X title %(t)s', {'t': 'index'})
        self.wview('primary', rset=rset)


class LocalizeCardView(PrimaryView):
    __select__ = PrimaryView.__select__ & is_instance('Card')

    def call(self, rset=None, **kwargs):
        rset = self.cw_rset or rset
        # Add links to content
        content = rset.get_entity(0, 0).content
        content = content % {'dataset-url': self._cw.build_url('dataset'),
                             'localizer-url': self._cw.build_url('localizer'),
                             'brainomics-url': self._cw.build_url('brainomics'),
                             'license-url': self._cw.build_url('license'),
                             'fmri-image': self._cw.data_url('dreamstime_s_33211444.jpg'),
                             'localizer-image': self._cw.data_url('dreamstime_s_28829039.jpg'),
                             'database-image': self._cw.data_url('dreamstime_s_32994616.jpg'),
                             'brainomics-image': self._cw.data_url('dreamstime_s_28730600.jpg'),
                             # Brainomics content
                             'subject-image': self._cw.data_url('images/subject.png'),
                             'images-image': self._cw.data_url('images/images.png'),
                             'genetics-image': self._cw.data_url('images/genetics.png'),
                             'questionnaire-image': self._cw.data_url('images/questionnaire.png'),
                             'subject-url': self._cw.build_url(rql='Any X WHERE X is Subject'),
                             'images-url': self._cw.build_url(rql='Any X, XT, XL, XI, XF, XD '
                                                              'WHERE X is Scan, '
                                                              'X type XT, X label XL, X identifier XI, '
                                                              'X format XF, X description XD'),
                             'genetics-url': self._cw.build_url(rql='(Any X WHERE X is GenomicMeasure) '
                                                                'UNION (Any X WHERE X is GenericTestRun, '
                                                                'X instance_of T, T type "genomics")'),
                             'questionnaire-url': self._cw.build_url(rql='Any X, XI, XD '
                                                                     'WHERE X is QuestionnaireRun, '
                                                                     'X identifier XI, X datetime XD'),
                             }
        self.w(content)


###############################################################################
### ACTIONS ###################################################################
###############################################################################
class LocalizerAction(Action):
    __regid__ = 'localizer'
    __select__ = yes()
    category = 'footer'
    order = 1
    title = _('Localizer dataset')

    def url(self):
        return self._cw.build_url('localizer')


class DatasetAction(Action):
    __regid__ = 'dataset'
    __select__ = yes()
    category = 'footer'
    order = 1
    title = _('Access dataset')

    def url(self):
        return self._cw.build_url('dataset')


class BrainomicsAction(Action):
    __regid__ = 'brainomics'
    __select__ = yes()
    category = 'footer'
    order = 1
    title = _('Brainomics project')

    def url(self):
        return self._cw.build_url('brainomics')


class LicenseAction(Action):
    __regid__ = 'license'
    __select__ = yes()
    category = 'footer'
    order = 2
    title = _('License')

    def url(self):
        return self._cw.build_url('license')


class LegalAction(Action):
    __regid__ = 'legal'
    __select__ = yes()
    category = 'footer'
    order = 2
    title = _('Legal')

    def url(self):
        return self._cw.build_url('legal')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (LocalizerIndexView, LocalizerDataZipAbstractView,
                       LocalizerDataZipAuthenticatedView,
                       LocalizerDataZipAnonymousView,
                       LocalizerScanZipFileBox))
    vreg.register_and_replace(LocalizerIndexView, BrainomicsIndexView)
    from cubicweb.web.views.actions import GotRhythmAction
    vreg.unregister(GotRhythmAction)
    from cubicweb.web.views.wdoc import HelpAction, AboutAction
    vreg.unregister(HelpAction)
    vreg.unregister(AboutAction)
    vreg.register_and_replace(LocalizerDataZipAuthenticatedView, DataZipAuthenticatedView)
    vreg.register_and_replace(LocalizerDataZipAnonymousView, DataZipAnonymousView)
    vreg.register_and_replace(LocalizerScanZipFileBox, ScanZipFileBox)

