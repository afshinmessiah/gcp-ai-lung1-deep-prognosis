"""
    ----------------------------------------
    IDC MedIA use case (GCP VM Demo)
    
    DeepPrognosis inference 
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    Modified: 06 FEB 21
    ----------------------------------------
    
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import sys
import yaml
import json
import argparse

import keras
import numpy as np
import pandas as pd

from my_lib.utils import *
from my_lib.data_utils import *
from patient_inference import patient_inference


# FIXME: this assumes the scripts are run in the src directory - document this?
base_conf_file_path = './config'
conf_file_list = [os.path.join(base_conf_file_path, f) for f in os.listdir(base_conf_file_path) if f.split('.')[-1] == 'yaml']

parser = argparse.ArgumentParser(description = 'Run DL inference for a single patient.')

parser.add_argument('--config',
                    required = False,
                    help = 'Specify the YAML configuration file containing the inference details.',
                    choices = conf_file_list,
                    default = './config/config.yaml'
                   )

parser.add_argument('--preproc_pat_dir',
                    required = True,
                    help = 'Specify the directory that stores the resampled NRRD files for the patient' \
                         + ' (output of "convert_pat.py").',
                   )


args = parser.parse_args()

conf_file_path = args.config
preproc_pat_dir_name = args.preproc_pat_dir

with open(conf_file_path) as f:
  yaml_conf = yaml.load(f, Loader = yaml.FullLoader)

# YAML config file - dataset
data_base_path = yaml_conf["data_base_path"]
model_base_path = yaml_conf["model_base_path"]

preproc_dataset_name = yaml_conf["preproc_dataset_name"]
preproc_dataset_path = os.path.join(data_base_path, preproc_dataset_name)
preproc_data_path = os.path.join(preproc_dataset_path, 'nrrd')

cohort_table_name = yaml_conf["cohort_table_name"]
cohort_table_path = os.path.join(data_base_path, cohort_table_name)
cohort_df = pd.read_csv(cohort_table_path)

preproc_pat_dir_path = os.path.join(preproc_data_path, preproc_pat_dir_name)
pat_df = cohort_df[cohort_df["PatientID"] == preproc_pat_dir_name]
pat = pat_df["PatientID"].values[0]

## ----------------------------------------

arch_json_name = yaml_conf["arch_json_name"]
arch_json_path = os.path.join(model_base_path, arch_json_name)

weights_name = yaml_conf["weights_name"]
weights_path = os.path.join(model_base_path, weights_name)
print('patient_inference(arch_json_path, weights_path, preproc_pat_dir_path, pat)')
print(arch_json_path, weights_path, preproc_pat_dir_path, pat)
w_dict = patient_inference(
    arch_json_path, weights_path, preproc_pat_dir_path, pat)
## ----------------------------------------

# define a new dataframe to store basics information + baseline output
# as well as the reproduced experiment output
df_keys = ['PatientID', 'ctStudyInstanceUID', 'ctSeriesInstanceUID',
           'rtstructSeriesInstanceUID', 'prob_logit_0', 'prob_logit_0']

data = {k : list() for k in df_keys}

# analysis results
res_df = pd.DataFrame(data, dtype = object)
res_csv_name = 'inference_res_' + preproc_pat_dir_name + '.csv'
res_csv_path = os.path.join(preproc_pat_dir_path, res_csv_name)

## ----------------------------------------

ct_res_crop_path = os.path.join(preproc_pat_dir_path, pat + '_ct_res_crop.nrrd')


w_dict["PatientID"] = pat

w_dict["ctStudyInstanceUID"] = pat_df["ctStudyInstanceUID"].values[0]
w_dict["ctSeriesInstanceUID"] = pat_df["ctSeriesInstanceUID"].values[0]
w_dict["rtstructSeriesInstanceUID"] = pat_df["rtstructSeriesInstanceUID"].values[0]

res_df = res_df.append(w_dict, ignore_index = True)

res_df.to_csv(res_csv_path, index = False)