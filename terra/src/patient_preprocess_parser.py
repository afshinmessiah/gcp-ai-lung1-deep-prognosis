"""
    ----------------------------------------
    IDC MedIA use case (GCP VM Demo)
    
    NRRD preprocessing for DeepPrognosis
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    Modified: 06 FEB 21
    ----------------------------------------
    
"""

import os
import sys
import yaml
import argparse

import pandas as pd
import SimpleITK as sitk

from my_lib.utils import *
from my_lib.data_utils import *
from patient_preprocess import patient_preprocess


# FIXME: this assumes the scripts are run in the src directory - document this?
base_conf_file_path = './config'
conf_file_list = [os.path.join(base_conf_file_path, f) for f in os.listdir(base_conf_file_path) if f.split('.')[-1] == 'yaml']

parser = argparse.ArgumentParser(description = 'Run NRRD preprocessing for a single patient.')

parser.add_argument('--config',
                    required = False,
                    help = 'Specify the YAML configuration file containing the run details.',
                    choices = conf_file_list,
                    default = './config/config.yaml'
                   )

parser.add_argument('--res_pat_dir',
                    required = True,
                    help = 'Specify the directory that stores the resampled NRRD files for the patient' \
                         + ' (output of "convert_pat.py").',
                   )


args = parser.parse_args()

conf_file_path = args.config
res_pat_dir_name = args.res_pat_dir

with open(conf_file_path) as f:
    yaml_conf = yaml.load(f, Loader = yaml.FullLoader)

# YAML config file - dataset
data_base_path = yaml_conf["data_base_path"]

preproc_dataset_name = yaml_conf["preproc_dataset_name"]
preproc_dataset_path = os.path.join(data_base_path, preproc_dataset_name)
preproc_data_path = os.path.join(preproc_dataset_path, 'nrrd')

cohort_table_name = yaml_conf["cohort_table_name"]
cohort_table_path = os.path.join(data_base_path, cohort_table_name)
cohort_df = pd.read_csv(cohort_table_path)

res_pat_dir_path = os.path.join(preproc_data_path, res_pat_dir_name)
pat_df = cohort_df[cohort_df["PatientID"] == res_pat_dir_name]
pat = pat_df["PatientID"].values[0]

## ----------------------------------------
    
# location where the tmp nrrd files (resampled CT/RTSTRUCT nrrd) should be saved
# by the "export_res_nrrd_from_dicom" function found in preprocess.py
res_ct_nrrd_path = os.path.join(res_pat_dir_path, pat + '_ct_resampled.nrrd')
res_rt_nrrd_path = os.path.join(res_pat_dir_path, pat + '_rt_resampled.nrrd')

# location where the nrrd files (cropped resampled CT/RTSTRUCT nrrd) should be saved
# by the "export_com_subvolume" function found in preprocess.py
ct_nrrd_crop_path = os.path.join(res_pat_dir_path, pat + '_ct_res_crop.nrrd')
rt_nrrd_crop_path = os.path.join(res_pat_dir_path, pat + '_rt_res_crop.nrrd')

patient_preprocess(
    res_ct_nrrd_path, res_rt_nrrd_path, ct_nrrd_crop_path, rt_nrrd_crop_path)
