#!/bin/bash

cd src

#python3 patient_convert.py --pat_dir '1.3.6.1.4.1.32722.99.99.239341353911714368772597187099978969331'
#python3 patient_preprocess.py --res_pat_dir LUNG1-001
#python3 patient_inference.py --preproc_pat_dir LUNG1-001

#python3 patient_convert.py --pat_dir '1.3.6.1.4.1.32722.99.99.203715003805996641695765332389135385095'
#python3 patient_preprocess.py --res_pat_dir LUNG1-002
#python3 patient_inference.py --preproc_pat_dir LUNG1-002

python3 patient_convert_parser.py --pat_dir '1.3.6.1.4.1.32722.99.99.247726286795860121686796574974227334270'
python3 patient_preprocess_parser.py --res_pat_dir LUNG1-003
python3 patient_inference_parser.py --preproc_pat_dir LUNG1-003
