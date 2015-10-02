#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# copyright 2015 CEA (Saclay, FRANCE), all rights reserved.
# contact http://brainomics.cea.fr -- mailto:localizer94@cea.fr

import os
import datetime
import json
import nibabel
import re
import csv
#~ from pprint import pprint


GENDER_MAP = {
    '1': 'male',
    '2': 'female',
}
GENDER_UNKOWN = 'unknown'

HANDEDNESS_MAP = {
    'Right handed': 'right',
    'Left handed': 'left',
    'Ambidextrous': 'ambidextrous',
}
HANDEDNESS_UNKOWN = 'unknown'

DEMOGRAPHICS = {
    'language',                 # str
    'schizophrenic',            # bool/None
    'dyslexic',                 # bool/None
    'dyscalculic',              # bool/None
    'synaesthete',              # bool/None
}

MRI_ISSUES = {
    'anatomy',                  # str/None
}

FMRI_ISSUES = {
    'epi_problem',              # bool/None
    'sound_problem',            # bool/None
    'video_problem',            # bool/None
    'motor_error',              # bool/None
}

SEQUENCE_TYPES = {
    'localizer_long_complex',   # bool/None
    'localizer_long_easy',      # bool/None
    'localizer_short_complex',  # bool/None
    'localizer_short_easy',     # bool/None
}

ADDITIONAL_INFO = (DEMOGRAPHICS | MRI_ISSUES | FMRI_ISSUES | SEQUENCE_TYPES)


def parse_subject_json(path):
    """Extract data from file subject.json pertaining to a subject.

    Parameters
    ----------
    path : str
        Full pathname of file suject.json related a subject.

    Returns
    -------
    nip : str
        ...
    family : str
        ...
    site : str
        ...
    subject : dict
        ...
    additional_info : dict
        ...

    """
    with open(path, 'r') as subject_json:
        subject_data = json.load(subject_json)
        nip = subject_data['nip']
        sex = subject_data['sex']
        age = subject_data['age']
        if age is not None:  # age is unknown for 4 subjects
            age = int(age)
        laterality = subject_data['laterality']
        family = subject_data['family']
        site = subject_data['site']
        protocol = subject_data['protocol']
        subject = {
            'identifier': nip,
            'code_in_study': nip,
            'gender': GENDER_MAP.get(sex, GENDER_UNKOWN),
            'handedness': HANDEDNESS_MAP.get(laterality, HANDEDNESS_UNKOWN),
        }
        additional_info = {k: subject_data[k] for k in ADDITIONAL_INFO}
        return nip, age, family, site, protocol, subject, additional_info


def parse_behavioural_json(path):
    """Extract data from file behavioural.json pertaining to a subject.

    Parameters
    ----------
    path : str
        Full pathname of file behavioural.json related a subject.

    Returns
    -------
    behavioural : dict
        ...

    """
    with open(path, 'r') as behavioural_json:
        subject_data = json.load(behavioural_json)
        del subject_data['date']
        return subject_data


def parse_nifti(path, tr_te=True):
    """Extract meta-data from a NIfTI file.
    """
    data = {}
    img = nibabel.load(path)
    data['shape_x'] = int(img.get_shape()[0])
    data['shape_y'] = int(img.get_shape()[1])
    data['shape_z'] = int(img.get_shape()[2])
    data['shape_t'] = int(img.get_shape()[3]) if len(img.get_shape()) == 4 else None
    data['voxel_res_x'] = float(img.get_header()['pixdim'][1])
    data['voxel_res_y'] = float(img.get_header()['pixdim'][2])
    data['voxel_res_z'] = float(img.get_header()['pixdim'][3])
    descrip = str(img.get_header()['descrip'])
    # Use descrip?
    try:
        if tr_te:
            tr, te = re.findall('TR=(.*)ms.*TE=(.*)ms', descrip)[0]
            data['tr'] = float(tr)
            data['te'] = float(te)
    except Exception as e:
        data['tr'] = None
        data['te'] = None
    return data


def parse_subject_dir(path):
    """Extract data from subject subdirectory.

    Parameters
    ----------
    path : str
        Full pathname of subject subdirectory.

    Returns
    -------
    nip : str
        ...
    family : str
        ...
    site : str
        ...
    subject : dict
        ...
    scans : dict
        ...
    questionnaires : dict
        ...

    """
    subject_json_path = os.path.join(path, 'subject.json')
    (nip, age, family, site, protocol, subject, additional_info) = parse_subject_json(subject_json_path)
    if nip != os.path.basename(path):
        pass  # ERROR

    demographics = {k: additional_info[k] for k in DEMOGRAPHICS}

    behavioural_json_path = os.path.join(path, 'behavioural.json')
    questionnaire = parse_behavioural_json(behavioural_json_path)
    questionnaire['language'] = 'French'
    questionnaires = [
        {
            'Assessment': {
                'identifier': nip + '_demographics',
                'age_of_subject': age,
                'timepoint': 'Baseline',
            },
            'Questionnaires': {
                'demographics': demographics,
            },
        },
        {
            'Assessment': {
                'identifier': nip + '_questionnaire',
                'age_of_subject': age,
                'timepoint': 'Baseline',
            },
            'Questionnaires': {
                'localizer_questionnaire': questionnaire,
            },
        },
    ]

    raw_anat_path = os.path.join(path, 'anat', 'raw_anat_defaced.nii.gz')
    raw_anat_data = parse_nifti(raw_anat_path)
    anat_path = os.path.join(path, 'anat', 'anat_defaced.nii.gz')
    anat_data = parse_nifti(anat_path)
    description = None
    if 'anatomy' in additional_info:
        description = additional_info['anatomy']
    anat_scans = [
        {
            'Scan': {
                'format': 'nii.gz',
                'identifier': nip + '_raw_anat',
                'label': 'raw anatomy',
                'type': 'raw T1',
                'description': description,
                'completed': True,
                'valid': True,
            },
            'TypeData': {
                'type': 'MRIData',
                'shape_x': raw_anat_data['shape_x'],
                'shape_y': raw_anat_data['shape_y'],
                'shape_z': raw_anat_data['shape_z'],
                'voxel_res_x': raw_anat_data['voxel_res_x'],
                'voxel_res_y': raw_anat_data['voxel_res_y'],
                'voxel_res_z': raw_anat_data['voxel_res_z'],
            },
            'FileSet': {
                'name': 'raw anatomy',
                'identifier': nip + '_raw_anat_file_set',
            },
            'ExternalResources': [
                {
                    'name': 'raw anatomy',
                    'identifier': nip + '_raw_anat_external_file',
                    'filepath': raw_anat_path,
                    'absolute_path': True,
                },
            ],
        },
        {
            'Scan': {
                'format': 'nii.gz',
                'identifier': nip + '_anat',
                'label': 'anatomy',
                'type': 'normalized T1',
                'description': description,
                'completed': True,
                'valid': True,
            },
            'TypeData': {
                'type': 'MRIData',
                'shape_x': anat_data['shape_x'],
                'shape_y': anat_data['shape_y'],
                'shape_z': anat_data['shape_z'],
                'voxel_res_x': anat_data['voxel_res_x'],
                'voxel_res_y': anat_data['voxel_res_y'],
                'voxel_res_z': anat_data['voxel_res_z'],
            },
            'FileSet': {
                'name': 'anatomy',
                'identifier': nip + '_anat_file_set',
            },
            'ExternalResources': [
                {
                    'name': 'anatomy',
                    'identifier': nip + '_anat_external_file',
                    'filepath': os.path.join(path, 'anat', 'anat_defaced.nii.gz'),
                    'absolute_path': True,
                },
            ],
        },
    ]

    raw_bold_path = os.path.join(path, 'fmri', 'raw_bold.nii.gz')
    raw_bold_data = parse_nifti(raw_bold_path)
    bold_path = os.path.join(path, 'fmri', 'bold.nii.gz')
    bold_data = parse_nifti(bold_path)
    description = None
    for k in FMRI_ISSUES:
        if k in additional_info and additional_info[k] is not None:
            if description:
                description += ' ' + k + '=' + str(additional_info[k])
            else:
                description = k + '=' + str(additional_info[k])
    for k in SEQUENCE_TYPES:
        if k in additional_info and additional_info[k]:
            if description:
                description += ' ' + k
            else:
                description = k
    fmri_scans = [
        {
            'Scan': {
                'format': 'nii.gz',
                'identifier': nip + '_raw_fmri',
                'label': 'raw bold',
                'type': 'raw fMRI',
                'description': description,
                'completed': True,
                'valid': True,
            },
            'TypeData': {
                'type': 'FMRIData',
                'shape_x': raw_bold_data['shape_x'],
                'shape_y': raw_bold_data['shape_y'],
                'shape_z': raw_bold_data['shape_z'],
                'shape_t': raw_bold_data['shape_t'],
                'voxel_res_x': raw_bold_data['voxel_res_x'],
                'voxel_res_y': raw_bold_data['voxel_res_y'],
                'voxel_res_z': raw_bold_data['voxel_res_z'],
            },
            'FileSet': {
                'name': 'preprocessed fMRI',
                'identifier': nip + '_raw_fmri_file_set',
            },
            'ExternalResources': [
                {
                    'name': 'preprocessed fMRI',
                    'identifier': nip + '_raw_fmri_external_file',
                    'filepath': raw_bold_path,
                    'absolute_path': True,
                },
            ],
        },
        {
            'Scan': {
                'format': 'nii.gz',
                'identifier': nip + '_fmri',
                'label': 'bold',
                'type': 'preprocessed fMRI',
                'description': description,
                'completed': True,
                'valid': True,
            },
            'TypeData': {
                'type': 'FMRIData',
                'shape_x': bold_data['shape_x'],
                'shape_y': bold_data['shape_y'],
                'shape_z': bold_data['shape_z'],
                'shape_t': bold_data['shape_t'],
                'voxel_res_x': bold_data['voxel_res_x'],
                'voxel_res_y': bold_data['voxel_res_y'],
                'voxel_res_z': bold_data['voxel_res_z'],
            },
            'FileSet': {
                'name': 'preprocessed fMRI',
                'identifier': nip + '_fmri_file_set',
            },
            'ExternalResources': [
                {
                    'name': 'preprocessed fMRI',
                    'identifier': nip + '_fmri_external_file',
                    'filepath': bold_path,
                    'absolute_path': True,
                },
            ],
        },
    ]

    c_maps_scans = []
    c_maps_dir = os.path.join(path, 'c_maps')
    for c_map in os.listdir(c_maps_dir):
        if not c_map.endswith('.nii.gz'):
            continue
        c_map_path = os.path.join(c_maps_dir, c_map)
        c_map_data = parse_nifti(c_map_path)
        label = c_map.replace('.nii.gz', '')
        identifier = nip + '_' + label.replace(' ', '_') + '_c_map'
        label = label.replace('_', ' ')
        scan = {
            'Scan': {
                'format': 'nii.gz',
                'identifier': identifier,
                'label': label,
                'type': 'c map',
                'completed': True,
                'valid': True,
            },
            'TypeData': {
                'type': 'FMRIData',
                'shape_x': c_map_data['shape_x'],
                'shape_y': c_map_data['shape_y'],
                'shape_z': c_map_data['shape_z'],
                'voxel_res_x': c_map_data['voxel_res_x'],
                'voxel_res_y': c_map_data['voxel_res_y'],
                'voxel_res_z': c_map_data['voxel_res_z'],
            },
            'FileSet': {
                'name': 'c map',
                'identifier': identifier + '_file_set',
            },
            'ExternalResources': [
                {
                    'name': 'c map',
                    'identifier': identifier + '_external_file',
                    'filepath': os.path.join(c_maps_dir, c_map),
                    'absolute_path': True,
                },
            ],
        }
        c_maps_scans.append(scan)

    t_maps_scans = []
    t_maps_dir = os.path.join(path, 't_maps')
    for t_map in os.listdir(t_maps_dir):
        if not t_map.endswith('.nii.gz'):
            continue
        t_map_path = os.path.join(t_maps_dir, t_map)
        t_map_data = parse_nifti(t_map_path)
        label = t_map.replace('.nii.gz', '')
        identifier = nip + '_' + label.replace(' ', '_') + '_t_map'
        label = label.replace('_', ' ')
        scan = {
            'Scan': {
                'format': 'nii.gz',
                'identifier': identifier,
                'label': label,
                'type': 't map',
                'completed': True,
                'valid': True,
            },
            'TypeData': {
                'type': 'FMRIData',
                'shape_x': t_map_data['shape_x'],
                'shape_y': t_map_data['shape_y'],
                'shape_z': t_map_data['shape_z'],
                'voxel_res_x': t_map_data['voxel_res_x'],
                'voxel_res_y': t_map_data['voxel_res_y'],
                'voxel_res_z': t_map_data['voxel_res_z'],
            },
            'FileSet': {
                'name': 't map',
                'identifier': identifier + '_file_set',
            },
            'ExternalResources': [
                {
                    'name': 'c map',
                    'identifier': identifier + '_external_file',
                    'filepath': os.path.join(c_maps_dir, t_map),
                    'absolute_path': True,
                },
            ],
        }
        t_maps_scans.append(scan)

    mask_path = os.path.join(path, 'mask.nii.gz')
    mask_data = parse_nifti(mask_path)
    mask_scans = [
        {
            'Scan': {
                'format': 'nii.gz',
                'identifier': nip + '_mask',
                'label': 'mask',
                'type': 'boolean mask',
                'completed': True,
                'valid': True,
            },
            'TypeData': {
                'type': 'MRIData',
                'shape_x': mask_data['shape_x'],
                'shape_y': mask_data['shape_y'],
                'shape_z': mask_data['shape_z'],
                'voxel_res_x': mask_data['voxel_res_x'],
                'voxel_res_y': mask_data['voxel_res_y'],
                'voxel_res_z': mask_data['voxel_res_z'],
            },
            'FileSet': {
                'name': 'mask',
                'identifier': nip + '_mask_file_set',
            },
            'ExternalResources': [
                {
                    'name': 'mask',
                    'identifier': nip + '_mask_external_file',
                    'filepath': mask_path,
                    'absolute_path': True,
                },
            ],
        },
    ]

    scans = [
        {
            'Assessment': {
                'identifier': nip + '_anat',
                'age_of_subject': age,
                'timepoint': 'Baseline',
            },
            'Scans': anat_scans,
        },
        {
            'Assessment': {
                'identifier': nip + '_fmri',
                'age_of_subject': age,
                'timepoint': 'Baseline',
            },
            'Scans': fmri_scans,
        },
        {
            'Assessment': {
                'identifier': nip + '_c_maps',
                'age_of_subject': age,
                'timepoint': 'Baseline',
            },
            'Scans': c_maps_scans,
        },
        {
            'Assessment': {
                'identifier': nip + '_t_maps',
                'age_of_subject': age,
                'timepoint': 'Baseline',
            },
            'Scans': t_maps_scans,
        },
        {
            'Assessment': {
                'identifier': nip + '_mask',
                'age_of_subject': age,
                'timepoint': 'Baseline',
            },
            'Scans': mask_scans,
        },
    ]

    return nip, family, site, subject, scans, questionnaires


def parse_subjects(path):
    """Extract data from directory containing subject subdirectories.

    Parameters
    ----------
    path : str
        Pathname of root directory.

    Returns
    -------
    dict
        Dictionary with subject meta-data, ready to be output to JSON.

    """
    subjects = {}
    subject_groups = {}
    questionnaires = {}
    scans = {}
    for subject in os.listdir(path):
        subject_dir = os.path.join(path, subject)
        if not os.path.isdir(subject_dir):
            continue
        (nip, family, site, subject, s, q) = parse_subject_dir(subject_dir)
        subjects[nip] = subject
        if family in subject_groups:
            subject_groups[family]['members'].append(nip)
        else:
            subject_groups[family] = {
                'identifier': family,
                'name': family,
                'type': 'family',
                'members': [nip],
            }
        if site not in scans:
            scans[site] = {}
        scans[site][nip] = s
        if site not in questionnaires:
            questionnaires[site] = {}
        questionnaires[site][nip] = q
    return subjects, subject_groups, scans, questionnaires


def parse_genetics(path, bed_bim_fam_basename):
    """Extract meta-data from the FAM file of a BED/BIM/FAM triplet.

    Parameters
    ----------
    path : str
        Pathname of directory containing BED/BIM/FAM triplet of files.

    bed_bim_fam_basename : str
        Basename of BED/BIM/FAM files.

    Returns
    -------
    dict
        Dictionary with genomics data, ready for JSON output.

    """
    fam_path = os.path.join(path, bed_bim_fam_basename + '.fam')
    fam_file = open(fam_path, 'rU')
    # read FAM file as CSV file
    fam_reader = csv.reader(fam_file, delimiter=' ')
    # one subject per line
    genetics = []
    for row in fam_reader:
        nip = row[1]
        measure = {
            'Assessment': {
                'identifier': nip + '_genetics',
                'timepoint': 'Baseline',
            },
            'GenomicMeasures': [
                {
                    'GenomicMeasure': {
                        'identifier': nip + '_genomic_measure',
                        'type': 'SNP',
                        'format': 'plink',
                        'chromset': 'all',
                    },
                },
            ],
        }
        genetics.append(measure)
    return genetics


def main():
    subjects_dir = ('/volatile/LOCALIZER/anonymized_2015-01-23/subjects')
    (subjects, subject_groups, scans, questionnaires) = parse_subjects(subjects_dir)

    today = datetime.date.today()

    subjects_file = ('/neurospin/brainomics/2012_brainomics_localizer/'
                     'export/json/subjects_{0}.json'
                     .format(today.isoformat()))
    with open(subjects_file, 'w') as output:
        json.dump(subjects, output, indent=4, separators=(',', ': '))
    subject_groups_file = ('/neurospin/brainomics/2012_brainomics_localizer/'
                           'export/json/subjectgroups_{0}.json'
                           .format(today.isoformat()))
    with open(subject_groups_file, 'w') as output:
        json.dump(subject_groups, output, indent=4, separators=(',', ': '))
    questionaires_file = ('/neurospin/brainomics/2012_brainomics_localizer/'
                          'export/json/questionaires_{0}.json'
                          .format(today.isoformat()))
    with open(questionaires_file, 'w') as output:
        json.dump(questionnaires, output, indent=4, separators=(',', ': '))
    scans_file = ('/neurospin/brainomics/2012_brainomics_localizer/'
                  'export/json/scans_{0}.json'
                  .format(today.isoformat()))
    with open(scans_file, 'w') as output:
        json.dump(scans, output, indent=4, separators=(',', ': '))

    genetics_dir = ('/volatile/LOCALIZER/anonymized_2015-01-23/genetics')
    genetics = parse_genetics(genetics_dir, 'Localizer94')

    genetics_file = ('/neurospin/brainomics/2012_brainomics_localizer/'
                     'export/json/genetics_{0}.json'
                     .format(today.isoformat()))
    with open(genetics_file, 'w') as output:
        json.dump(genetics, output, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    main()
