"""
    ----------------------------------------
    IDC MedIA use case (GCP VM Demo)
    
    DICOM to NRRD conversion 
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


# FIXME: this assumes the scripts are run in the src directory - document this?
base_conf_file_path = './config'
conf_file_list = [os.path.join(base_conf_file_path, f) for f in os.listdir(base_conf_file_path) if f.split('.')[-1] == 'yaml']

parser = argparse.ArgumentParser(description = 'Run DICOM to NRRD conversion for a single patient.')

parser.add_argument('--config',
                    required = False,
                    help = 'Specify the YAML configuration file containing the run details.',
                    choices = conf_file_list,
                    default = './config/config.yaml'
                   )

parser.add_argument('--pat_dir',
                    required = True,
                    help = 'Specify the directory that stores the DICOM and RTSTRUCT series for the patient' \
                         + ' (named after ctStudyInstanceUID).',
                   )


args = parser.parse_args()

conf_file_path = args.config
pat_dir_name = args.pat_dir

with open(conf_file_path) as f:
  yaml_conf = yaml.load(f, Loader = yaml.FullLoader)

# YAML config file - dataset
data_base_path = yaml_conf["data_base_path"]
dataset_name = yaml_conf["dataset_name"]

dataset_path = os.path.join(data_base_path, dataset_name)
data_path = os.path.join(dataset_path, 'dicom')

preproc_dataset_name = yaml_conf["preproc_dataset_name"]
preproc_dataset_path = os.path.join(data_base_path, preproc_dataset_name)
preproc_data_path = os.path.join(preproc_dataset_path, 'nrrd')

cohort_table_name = yaml_conf["cohort_table_name"]
cohort_table_path = os.path.join(data_base_path, cohort_table_name)
cohort_df = pd.read_csv(cohort_table_path)

pat_dir_path = os.path.join(data_path, pat_dir_name)
pat_df = cohort_df[cohort_df["ctStudyInstanceUID"] == pat_dir_name]
pat = pat_df["PatientID"].values[0]

## ----------------------------------------

pat_out_path = os.path.join(preproc_data_path, pat)
  
if not os.path.exists(pat_out_path):
  os.makedirs(pat_out_path)
  
# location where the tmp nrrd files (resampled CT/RTSTRUCT nrrd) should be saved
# by the "export_res_nrrd_from_dicom" function found in preprocess.py
res_ct_nrrd_path = os.path.join(pat_out_path, pat + '_ct_resampled.nrrd')
res_rt_nrrd_path = os.path.join(pat_out_path, pat + '_rt_resampled.nrrd')
  
## ----------------------------------------
  
pat_df = cohort_df[cohort_df["PatientID"] == pat]

path_to_ct_dir = os.path.join(pat_dir_path, pat_df["ctSeriesInstanceUID"].values[0])
path_to_rt_dir = os.path.join(pat_dir_path, pat_df["rtstructSeriesInstanceUID"].values[0])

# sanity check
assert os.path.exists(path_to_ct_dir)
assert os.path.exists(path_to_rt_dir)
    
## ----------------------------------------
  
try:
  proc_log = export_res_nrrd_from_dicom(dicom_ct_path = path_to_ct_dir, 
                                        dicom_rt_path = path_to_rt_dir, 
                                        output_dir = pat_out_path,
                                        ct_interpolation = 'linear',
                                        pat_id = pat,
                                        output_dtype = "float")

except Exception as e:
  print(e)
  sys.exit(-1)

## ----------------------------------------
  
# check every step of the DICOM to NRRD conversion returned 0 (everything's ok)
assert(np.sum(np.array(list(proc_log.values()))) == 0)
  
# sanity check - resampled NRRD files were created
assert(os.path.exists(res_ct_nrrd_path))
assert(os.path.exists(res_rt_nrrd_path))
  
sitk_vol = sitk.ReadImage(res_ct_nrrd_path)
vol = sitk.GetArrayFromImage(sitk_vol)
  
sitk_seg = sitk.ReadImage(res_rt_nrrd_path)
seg = sitk.GetArrayFromImage(sitk_seg)
  
# sanity check
assert(vol.shape == seg.shape)