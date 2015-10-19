# -*- coding: utf-8 -*-
# copyright 2015 CEA (Saclay, FRANCE), all rights reserved.
# contact http://brainomics.cea.fr/ -- mailto:localizer94@cea.fr

"""cubicweb-localizer schema"""

GENOMIC_FILEPATH_PERMISSIONS = {
    'read': (u'managers',),
    'update': (u'managers',),
}

def post_build_callback(schema):
    # genomic measures must not be downloaded
    rdef = schema['GenomicMeasure'].rdef('filepath')
    rdef.permissions = GENOMIC_FILEPATH_PERMISSIONS
