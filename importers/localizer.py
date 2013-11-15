# -*- coding: utf-8 -*-

import sys
import os
import os.path as osp
import re
import glob
import csv
import json
import pickle
from datetime import datetime

import nibabel as nb

from cubes.brainomics.importers.helpers import (get_image_info, import_genes,
                                                import_chromosomes, import_snps)


###############################################################################
### Global Mappings ###########################################################
###############################################################################
GENDER_MAP = {
    '1': u'male',
    '2': u'female',
    '3': u'unknown',
}

HANDEDNESS_MAP = {
    'Right handed': u'right',
    'Left handed': u'left',
    'Ambidextrous': u'ambidextrous',
    'Unknown': u'unknown',
}

SCORE_TYPES = (
    u'language',
    u'family',
    u'schizophrenic',
    u'dyslexic',
    u'dyscalculic',
    u'synaesthete',
)

SEQ_TYPES = (
    u'localizer_long_complex',
    u'localizer_long_easy',
    u'localizer_short_complex',
    u'localizer_short_easy',
)


###############################################################################
### MedicalExp entities #######################################################
###############################################################################
def import_subject(data_dir):
    """Import a subject from a data dir"""
    data, score_values = {}, []
    info = json.load(open('%s/subject.json' % data_dir))
    data['identifier'] = info['nip']
    # age varies with time: it should not be stored as an attribute of Subject
    # keep it for later use: store as an attribute of Assessment
    age_for_assessment = info['age']
    data['gender'] = GENDER_MAP.get(info['sex'], GENDER_MAP['3'])
    data['handedness'] = HANDEDNESS_MAP.get(info['laterality'],
                                            HANDEDNESS_MAP['Unknown'])
    for score in SCORE_TYPES:
        score_values.append({'name': score,
                             'value': info.get(score)})
    return data, age_for_assessment, score_values

def import_study(data_dir):
    """Import a study from a data dir"""
    data = {}
    data['data_filepath'] = osp.abspath(data_dir)
    data['name'] = u'localizer'
    data['description'] = u'localizer db'
    return data

def import_center(data_dir):
    """Import a center"""
    data = {}
    info = json.load(open('%s/subject.json' % data_dir))
    data['identifier'] = info['site']
    if info['site'] == u'SHFJ':
        data['name'] = u'SHFJ'
        data['department'] = u'Essonne'
        data['city'] = u'Orsay'
        data['country'] = u'France'
    elif info['site'] == u'Neurospin':
        data['name'] = u'Neurospin'
        data['department'] = u'Essonne'
        data['city'] = u'Gif-sur-Yvette'
        data['country'] = u'France'
    return data

def import_device(data_dir):
    """Import a device"""
    data = {}
    info = json.load(open('%s/subject.json' % data_dir))
    if info['site'] == u'Neurospin':
        data['name'] = '3T SIEMENS Trio'
        data['manufacturer'] = 'SIEMENS'
        data['model'] = 'Trio'
        data['hosted_by'] = 'Neurospin'
    if info['site'] == u'SHFJ':
        data['name'] = '3T Brucker'
        data['manufacturer'] = 'Brucker'
        data['model'] = '3T Brucker'
        data['hosted_by'] = 'SHFJ'
    return data

def import_assessment(data_dir, age_for_assessment, label, study_eid):
    """Import an assessment"""
    info = json.load(open('%s/subject.json' % data_dir))
    data = {}
    data['identifier'] = u'%s_%s' % (info['nip'], label)
    data['protocol'] = info['protocol']
    data['age_for_assessment'] = age_for_assessment
    data['timepoint'] = info['date']
    data['related_study'] = study_eid
    if info.get('date'):
        data['datetime'] = datetime.strptime(info['date'],
                                             '%Y-%m-%d %H:%M:%S')
    else:
        data['datetime'] = None
    return data


###############################################################################
### Neuroimaging entities #####################################################
###############################################################################
def import_neuroimaging(data_dir, dtype='anat', norm_prep=False):
    """Import a neuorimaging scan"""
    scan_data, mri_data = {}, {}
    info = json.load(open('%s/subject.json' % data_dir))
    # Label and id
    if dtype == 'anat':
        mri_data['sequence'] = u'T1'
        scan_data['identifier'] = u'%s_anat' % info['exam']
        scan_data['label'] = u'anatomy' if normalized else u'raw anatomy'
        scan_data['type'] = u'normalized T1' if norm_prep else u'raw T1'
        if norm_prep:
            scan_data['filepath'] = os.path.join(data_dir, 'anat', 'anat_defaced.nii.gz')
        else:
            scan_data['filepath'] = os.path.join(data_dir, 'anat', 'raw_anat_defaced.nii.gz')
    else:
        mri_data['sequence'] = u'EPI'
        scan_data['identifier'] = u'%s_fmri' % info['exam'] if norm_prep  \
                                  else u'%s_raw_fmri' % info['exam']
        scan_data['label'] = u'bold' if norm_prep else u'raw bold'
        scan_data['type'] = u'preprocessed fMRI' if norm_prep else u'raw fMRI'
        if norm_prep:
            scan_data['filepath'] = os.path.join(data_dir, 'fmri', 'bold.nii.gz')
        else:
            scan_data['filepath'] = os.path.join(data_dir, 'fmri', 'raw_bold.nii.gz')
    # Data properties
    scan_data['format'] = u'nii.gz'
    scan_data['timepoint'] = info['date']
    scan_data['completed'] = True
    scan_data['valid'] = True
    # Description
    if dtype == 'anat':
        scan_data['description'] = info['anatomy']
    else:
        scan_data['description'] = (
            u'epi_problem=%(epi_problem)s '
            'sound_problem=%(sound_problem)s '
            'video_problem=%(video_problem)s '
            'motor_error=%(motor_error)s' % info)
        for seq_type in SEQ_TYPES:
            if info[seq_type]:
                scan_data['description'] += u' %s' % seq_type
    # Update mri data
    mri_data.update(get_image_info(scan_data['filepath']))
    return scan_data, mri_data

def import_maps(data_dir, dtype='c'):
    """Import c/t maps"""
    info = json.load(open('%s/subject.json' % data_dir))
    base_path = os.path.join(data_dir, '%s_maps' % dtype)
    for img_path in glob.iglob(os.path.join(base_path, '*.nii.gz')):
        scan_data, mri_data = {}, {}
        scan_data['identifier'] = u'%s_%s_map' % (info['exam'], dtype)
        scan_data['label'] = unicode(os.path.split(img_path)[1].split(
            '.nii.gz')[0].replace('_', ' '))
        scan_data['format'] = u'nii.gz'
        scan_data['type'] = u'%s map' % dtype
        scan_data['filepath'] = img_path
        scan_data['timepoint'] = info['date']
        scan_data['completed'] = True
        scan_data['valid'] = True
        # Mri data
        mri_data['sequence'] = None
        mri_data.update(get_image_info(scan_data['filepath'], get_tr=False))
        name = os.path.split(img_path)[1].split('.nii.gz')[0]
        ext_resource = {}
        ext_resource['name'] = u'contrast definition'
        ext_resource['filepath'] = unicode(os.path.join(data_dir,
                                                        'contrasts',
                                                        '%s.json' % name))
        yield scan_data, mri_data, ext_resource

def import_mask(data_dir):
    """Import a mask"""
    scan_data, mri_data = {}, {}
    info = json.load(open('%s/subject.json' % data_dir))
    scan_data['identifier'] = u'%s_mask' % info['exam']
    scan_data['label'] = u'mask'
    scan_data['format'] = u'nii.gz'
    scan_data['type'] = u'boolean mask'
    scan_data['filepath'] = unicode(os.path.join(data_dir, 'mask.nii.gz'))
    scan_data['timepoint'] = info['date']
    scan_data['completed'] = True
    scan_data['valid'] = True
    mri_data['sequence'] = None
    mri_data.update(get_image_info(scan_data['filepath']))
    return scan_data, mri_data


###############################################################################
### Questionnaire entities ####################################################
###############################################################################
def import_questionnaire(data_dir):
    """Import a questionnaire and its questions"""
    questionnaire = {}
    questionnaire['name'] = u'localizer questionnaire'
    questionnaire['identifier'] = u'localizer_questionnaire'
    questionnaire['type'] = u'behavioural'
    questionnaire['version'] = u'1.0'
    questionnaire['language'] = u'French'
    behave = json.load(open('%s/behavioural.json' % data_dir))
    del behave['date']
    # Questions
    questions = []
    values = [behave[k] for k in sorted(behave.keys())]
    for i, (val, item) in enumerate(zip(values, sorted(behave.keys()))):
        question = {}
        question['identifier'] = u'localizer_%s' % i
        question['position'] = i
        question['text'] = unicode(item)
        question['type'] = u'boolean' if isinstance(val, bool) else u'float'
        question['possible_answers'] = None
        questions.append(question)
    return questionnaire, questions

def import_questionnaire_run(data_dir, questionnaire_id, questions_id):
    """Import a questionnaire run"""
    run = {}
    behave = json.load(open('%s/behavioural.json' % data_dir))
    sid = os.path.split(data_dir)[1]
    run['identifier'] = u'localizer_questionnaire_%s' % (sid)
    run['user_ident'] = u'subject'
    if behave.get('date'):
        run['datetime'] = datetime.strptime(
            behave['date'],
            '%Y-%m-%d %H:%M:%S')
    else:
        run['datetime'] = None
    del behave['date']
    del behave['nip']
    run['iteration'] = 1
    run['completed'] = True
    run['valid'] = True
    run['instance_of'] = questionnaire_id
    # Answers
    answers = []
    values = [behave[k] for k in sorted(behave.keys())]
    for i, (val, item) in enumerate(zip(values, sorted(behave.keys()))):
        answer = {}
        # XXX: handle str answers
        if not isinstance(val, (str, unicode)):
            answer['value'] = float(val) if val else None
            answer['datetime'] = run['datetime']
            answer['question'] = questions_id[item]
            answers.append(answer)
    return run, answers


###############################################################################
### Genomics entities #########################################################
###############################################################################
# XXX These functions may be pushed in helpers, as they may be more general
def import_genomic_measures(measure_path, genetics_basename):
    """Import a genomic measures"""
    g_measures = {}
    # path to BED / BIM / FAM files
    bed_path = os.path.join(measure_path, genetics_basename + '.bed')
    bim_path = os.path.join(measure_path, genetics_basename + '.bim')
    fam_path = os.path.join(measure_path, genetics_basename + '.fam')
    # read FAM file as CSV file
    fam_file = open(fam_path, 'rU')
    fam_reader = csv.reader(fam_file, delimiter=' ')
    # one subject per line
    for row in fam_reader:
        subject_id = row[1]
        genomic_measure = {}
        genomic_measure['identifier'] = u'genomic_measure_%s' % subject_id
        genomic_measure['type'] = u'SNP'
        genomic_measure['format'] = u'plink'
        genomic_measure['filepath'] = unicode(bed_path)
        genomic_measure['chip_serialnum'] = None
        genomic_measure['completed'] = True
        genomic_measure['valid'] = True
        genomic_measure['platform'] = None
        g_measures[subject_id] = genomic_measure
    return g_measures


###############################################################################
### MAIN ######################################################################
###############################################################################
if __name__ == '__main__':
    # Create store
    from cubicweb.dataimport import SQLGenObjectStore
    store = SQLGenObjectStore(session)
    sqlgen_store = True

    root_dir = osp.abspath(sys.argv[4])
    subjects_dir = osp.join(root_dir, 'subjects')
    genetics_dir = osp.join(root_dir, 'genetics')

    ### Study #################################################################
    study = import_study(data_dir=root_dir)
    study = store.create_entity('Study', **study)

    ### Initialize questionnaire ##############################################
    one_subject = glob.glob('%s/*' % subjects_dir)[0]
    questionnaire, questions = import_questionnaire(one_subject)
    questionnaire = store.create_entity('Questionnaire', **questionnaire)
    questions_id = {}
    for question in questions:
        question['questionnaire'] = questionnaire.eid
        question = store.create_entity('Question', **question)
        questions_id[question.text] = question.eid

    ### Initialize genetics ####################################################
    # Chromosomes
    chrs = import_chromosomes(os.path.join(genetics_dir, 'chromosomes.json'))
    chr_map = {}
    for _chr in chrs:
        print 'chr', _chr['name']
        _chr = store.create_entity('Chromosome', **_chr)
        chr_map.setdefault(_chr['name'], _chr.eid)
    # Genes
    genes = import_genes(os.path.join(genetics_dir, 'chromosomes.json'),
                         os.path.join(genetics_dir, 'hg18.refGene.meta'))
    for gene in genes:
        print 'gene', gene['name'], gene['chromosome']
        gene['chromosome'] = chr_map[gene['chromosome']]
        gene = store.create_entity('Gene', **gene)
    # Flush/Commit
    if sqlgen_store:
        store.flush()
    # Snps
    snps = import_snps(os.path.join(genetics_dir, 'chromosomes.json'),
                       os.path.join(genetics_dir, 'Localizer94.bim'))
    snp_eids = []
    for ind, snp in enumerate(snps):
        print 'snp', snp['rs_id']
        snp['chromosome'] = chr_map[snp['chromosome']]
        snp = store.create_entity('Snp', **snp)
        snp_eids.append(snp.eid)
        if sqlgen_store and ind and ind % 100000 == 0:
            store.flush()
    # Flush/Commit
    if sqlgen_store:
        store.flush()
    # Platform
    platform = {'identifier': 'Affymetrix_6.0'}
    platform = store.create_entity('GenomicPlatform', **platform)
    for snp_eid in snp_eids:
        store.relate(platform.eid, 'related_snps', snp_eid)

    ### Genetics measures #####################################################
    gen_measures = import_genomic_measures(genetics_dir, 'Localizer94')

    # Flush/Commit
    if sqlgen_store:
        store.flush()

    ###########################################################################
    ### Subjects ##############################################################
    ###########################################################################
    centers, devices, score_defs = {}, {}, {}
    for sid in glob.glob('%s/*' % subjects_dir):

        print '-------->', sid, os.path.split(sid)[1]

        # Centers #############################################################
        center = import_center(sid)
        if center['name'] not in centers:
            center = store.create_entity('Center', **center)
            centers.setdefault(center.name, center.eid)
            center_eid = center.eid
        else:
            center_eid = centers[center['name']]

        # Devices #############################################################
        device = import_device(sid)
        device['hosted_by'] = centers[device['hosted_by']]
        if device['name'] not in devices:
            device = store.create_entity('Device', **device)
            devices.setdefault(device.name, device.eid)
            device_id = device.eid
        else:
            device_id = devices[device['name']]

        # Subject #############################################################
        subject, age_for_assessment, score_values = import_subject(sid)
        subject = store.create_entity('Subject', **subject)
        store.relate(subject.eid, 'related_studies', study.eid)
        for score_val in score_values:
            value = score_val['value']
            if not value:
                continue
            if score_val['name'] in score_defs:
                def_eid = score_defs.get(score_val['name'])
            else:
                score_def = {}
                score_def['name'] = score_val['name']
                score_def['category'] = u'demographics'
                score_def['type'] = u'string'
                score_def = store.create_entity('ScoreDefinition', **score_def)
                score_defs[score_val['name']] = score_def.eid
                def_eid = score_def.eid
            score_val = store.create_entity('ScoreValue', definition=def_eid,
                                            text=value)
            store.relate(subject.eid, 'related_infos', score_val.eid)

        # Design matrix #######################################################
        dm_res = store.create_entity('ExternalResource',
                                     name=u'design_matrix',
                                     related_study=study.eid,
                                     filepath=unicode(osp.relpath(
                                         os.path.join(sid, 'design_matrix.json'),
                                         start=root_dir)))

        # Genetics ############################################################
        gen_assessment = import_assessment(sid, age_for_assessment, 'genetics', study.eid)
        gen_assessment = store.create_entity('Assessment', **gen_assessment)
        store.relate(center_eid, 'holds', gen_assessment.eid)
        store.relate(subject.eid, 'concerned_by', gen_assessment.eid)
        measure = gen_measures[subject.identifier]
        measure['platform'] = platform.eid
        measure['related_study'] = study.eid
        measure['filepath'] = osp.relpath(measure['filepath'], start=root_dir)
        measure = store.create_entity('GenomicMeasure', **measure)
        store.relate(measure.eid, 'concerns', subject.eid, subjtype='GenomicMeasure')
        store.relate(gen_assessment.eid, 'generates', measure.eid, subjtype='Assessment')

        # Anat & fMRI ############################################################
        # anat assessment
        anat_assessment = import_assessment(sid, age_for_assessment, 'anat', study.eid)
        anat_assessment = store.create_entity('Assessment', **anat_assessment)
        store.relate(center_eid, 'holds', anat_assessment.eid)
        store.relate(subject.eid, 'concerned_by', anat_assessment.eid)
        for normalized in (False, True):
            scan_anat, mri_anat = import_neuroimaging(sid, 'anat', normalized)
            mri_anat = store.create_entity('MRIData', **mri_anat)
            scan_anat['has_data'] = mri_anat.eid
            scan_anat['related_study'] = study.eid
            # Get the relative filepath
            scan_anat['filepath'] = osp.relpath(scan_anat['filepath'], start=root_dir)
            scan_anat = store.create_entity('Scan', **scan_anat)
            store.relate(scan_anat.eid, 'concerns', subject.eid, subjtype='Scan')
            store.relate(scan_anat.eid, 'uses_device', device_id)
            store.relate(anat_assessment.eid, 'generates', scan_anat.eid, subjtype='Assessment')
        # fmri assessment
        fmri_assessment = import_assessment(sid, age_for_assessment, 'fmri', study.eid)
        fmri_assessment = store.create_entity('Assessment', **fmri_assessment)
        store.relate(center_eid, 'holds', fmri_assessment.eid)
        store.relate(subject.eid, 'concerned_by', fmri_assessment.eid)
        for preprocessed in (False, True):
            scan_fmri, mri_fmri = import_neuroimaging(sid, 'fmri', preprocessed)
            mri_fmri = store.create_entity('MRIData', **mri_fmri)
            scan_fmri['has_data'] = mri_fmri.eid
            scan_fmri['related_study'] = study.eid
            # Get the relative filepath
            scan_fmri['filepath'] = osp.relpath(scan_fmri['filepath'], start=root_dir)
            scan_fmri = store.create_entity('Scan', **scan_fmri)
            store.relate(scan_fmri.eid, 'concerns', subject.eid, subjtype='Scan')
            store.relate(scan_fmri.eid, 'uses_device', device_id)
            store.relate(fmri_assessment.eid, 'generates', scan_fmri.eid, subjtype='Assessment')

        # c-maps & t-maps #####################################################
        for dtype, label in (('c', 'c_maps'), ('t', 't_maps')):
            assessment = import_assessment(sid, age_for_assessment, label, study.eid)
            assessment = store.create_entity('Assessment', **assessment)
            store.relate(center_eid, 'holds', assessment.eid)
            store.relate(subject.eid, 'concerned_by', assessment.eid)
            for scan, mri, con_res in import_maps(sid, dtype):
                mri = store.create_entity('MRIData', **mri)
                if con_res:
                    con_res['related_study'] = study.eid
                    con_res['filepath'] = osp.relpath(con_res['filepath'], start=root_dir)
                    con_res = store.create_entity('ExternalResource', **con_res)
                scan['has_data'] = mri.eid
                scan['related_study'] = study.eid
                # Get the relative filepath
                scan['filepath'] = osp.relpath(scan['filepath'], start=root_dir)
                scan = store.create_entity('Scan', **scan)
                store.relate(scan.eid, 'concerns', subject.eid, subjtype='Scan')
                store.relate(scan.eid, 'uses_device', device_id)
                store.relate(assessment.eid, 'generates', scan.eid, subjtype='Assessment')
                store.relate(scan.eid, 'external_resources', con_res.eid)
                store.relate(scan.eid, 'external_resources', dm_res.eid)

        # mask ################################################################
        assessment = import_assessment(sid, age_for_assessment, 'mask', study.eid)
        assessment = store.create_entity('Assessment', **assessment)
        store.relate(center_eid, 'holds', assessment.eid)
        store.relate(subject.eid, 'concerned_by', assessment.eid)
        scan, mri = import_mask(sid)
        mri = store.create_entity('MRIData', **mri)
        scan['has_data'] = mri.eid
        scan['related_study'] = study.eid
        # Get the relative filepath
        scan['filepath'] = osp.relpath(scan['filepath'], start=root_dir)
        scan = store.create_entity('Scan', **scan)
        store.relate(scan.eid, 'concerns', subject.eid, subjtype='Scan')
        store.relate(scan.eid, 'uses_device', device_id)
        store.relate(assessment.eid, 'generates', scan.eid, subjtype='Assessment')

        # Questionnaire run ###################################################
        assessment = import_assessment(sid, age_for_assessment, 'questionnaire', study.eid)
        assessment = store.create_entity('Assessment', **assessment)
        store.relate(center_eid, 'holds', assessment.eid)
        store.relate(subject.eid, 'concerned_by', assessment.eid)
        run, answers = import_questionnaire_run(sid, questionnaire.eid, questions_id)
        run['related_study'] = study.eid
        run = store.create_entity('QuestionnaireRun', **run)
        # Answers
        for answer in answers:
            answer['questionnaire_run'] = run.eid
            answer = store.create_entity('Answer', **answer)
        store.relate(run.eid, 'concerns', subject.eid, subjtype='QuestionnaireRun')
        store.relate(assessment.eid, 'generates', run.eid, subjtype='Assessment')

    # Flush/Commit
    if sqlgen_store:
        store.flush()
    store.commit()
