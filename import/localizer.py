#! /usr/bin/env python
# -*- coding: utf-8 -*-

# copyright 2015 CEA (Saclay, FRANCE), all rights reserved.
# contact http://brainomics.cea.fr -- mailto:localizer94@cea.fr

STUDY_NAME = "Localizer"
STUDY_PATH = "/volatile/LOCALIZER/anonymized_2013-07-25"


import os
import sys
import getpass
import json
from cubicweb import cwconfig
from cubicweb.dbapi import in_memory_repo_cnx


def main():
    # instance name & login information
    default = 'localizer'
    instance_name = raw_input('Enter the instance name '
                              '[default: ' + default + ']: ')
    if not instance_name:
        instance_name = default
    default = '~/.virtualenvs/localizer/git/piws'
    piws_path = raw_input('Enter the PIWS cube path '
                          '[default: ' + default + ']: ')
    if not piws_path:
        piws_path = os.path.expanduser(default)

    # subjects
    default = ('/neurospin/brainomics/2012_brainomics_localizer/'
               'export/json/subjects_2015-10-20.json')
    subjects_file = raw_input('Enter the path to subjects data '
                              '[default: ' + default + ']: ')
    if not subjects_file:
        subjects_file = default
    default = ('/neurospin/brainomics/2012_brainomics_localizer/'
               'export/json/subjectgroups_2015-10-20.json')
    subjectgroups_file = raw_input('Enter the path to subject groups data '
                                   '[default: ' + default + ']: ')
    if not subjectgroups_file:
        subjectgroups_file = default

    # scans
    default = ('/neurospin/brainomics/2012_brainomics_localizer/'
               'export/json/scans_2015-10-20.json')
    scans_file = raw_input('Enter the path to scans '
                           '[default: ' + default + ']: ')
    if not scans_file:
        scans_file = default

    # demographics and questionnaires
    default = ('/neurospin/brainomics/2012_brainomics_localizer/'
               'export/json/questionaires_2015-10-20.json')
    questionnaires_file = raw_input('Enter the path to questionnaire data'
                                    '[default: ' + default + ']: ')
    if not questionnaires_file:
        questionnaires_file = default

    # genetics
    default = ('/neurospin/brainomics/2012_brainomics_localizer/'
               'export/json/genetics_2015-10-20.json')
    genetics_file = raw_input('Enter the path to genetics data '
                              '[default: ' + default + ']: ')
    if not genetics_file:
        genetics_file = default

    # login information
    default = 'admin'
    login = raw_input('Enter the "{0}" login '
                      '[default: '.format(instance_name) + default + ']: ')
    if not login:
        login = default
    default = 'admin'
    password = getpass.getpass('Enter the "{0}" password '
                               '[default: '.format(instance_name)
                               + default + ']: ')
    if not password:
        password = default

    # import PIWS
    sys.path.append(os.path.expanduser(piws_path))
    from piws.importer.subjects import Subjects
    from piws.importer.scans import Scans
    from piws.importer.questionnaires import Questionnaires
    from piws.importer.genetics import Genetics
    from piws.importer.processings import Processings

    # create a CubicWeb session
    config = cwconfig.instance_configuration(instance_name)
    repo, cnx = in_memory_repo_cnx(config, login=login, password=password)
    session = repo._get_session(cnx.sessionid)

    # parse JSON files
    with open(subjects_file) as infile:
        subjects = json.load(infile)
    with open(subjectgroups_file) as infile:
        subjectgroups = json.load(infile)
    with open(scans_file) as infile:
        scans = json.load(infile)
    with open(questionnaires_file) as infile:
        questionnaires = json.load(infile)
    with open(genetics_file) as infile:
        genetics = json.load(infile)

    # --
    db_subject_importer = Subjects(
        session, STUDY_NAME, subjects, use_store=True)
    db_subject_importer.import_data()
    db_subject_importer.cleanup()
    # -- scans
    if 1:
        for center, cscans in scans.iteritems():
            db_scan_importer = Scans(
                session, STUDY_NAME, center, cscans,
                can_read=True, can_update=False,
                data_filepath=STUDY_PATH, use_store=True,
                piws_security_model=False)
            db_scan_importer.import_data()
            db_scan_importer.cleanup()
    # -- questionnaires
    if 1:
        for center, cquestionnaires in questionnaires.iteritems():
            db_questionnaire_importer = Questionnaires(
                session, STUDY_NAME, center, cquestionnaires, can_read=True,
                can_update=False, data_filepath=STUDY_PATH, use_store=True,
                piws_security_model=False)
            db_questionnaire_importer.import_data()
            db_questionnaire_importer.cleanup()
    # -- genetics
    if 1:
        for center, cgenetics in genetics.iteritems():
            db_genetic_importer = Genetics(
                session, STUDY_NAME, center, genetics, can_read=True,
                can_update=False, data_filepath=STUDY_PATH, use_store=True,
                piws_security_model=False)
            db_genetic_importer.import_data()
            db_genetic_importer.cleanup()
    # -- processings
    if 0:
        db_processings_importer = Processings(
            session, STUDY_NAME, GENETIC_CENTER, processed_genetics, can_read=True,
            can_update=False, data_filepath=STUDY_PATH, use_store=True,
            piws_security_model=False)
        db_processings_importer.import_data()
        db_processings_importer.cleanup()

    # Commit
    session.commit()


if __name__ == "__main__":
    main()
