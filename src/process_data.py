"""
    ----------------------------------------
    IDC MedIA use case (GCP Demo)
    
    data processing
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    Modified: 01 DEC 20
    ----------------------------------------
    
"""

import os
import sys
import json
import keras
import numpy as np
import pandas as pd

from my_lib.utils import *
from my_lib.data_utils import *

## ----------------------------------------

data_base_path = '../data'
model_base_path = '../models'
output_base_path = '../outputs'

## ----------------------------------------

dataset_name = 'nsclc-radiomics'

preproc_dataset_name = dataset_name + '_preprocessed'
preproc_dataset_path = os.path.join(data_base_path, preproc_dataset_name)
preproc_data_path = os.path.join(preproc_dataset_path, 'nrrd')

csv_out_name = 'nsclc-radiomics_preproc_details.csv'
dataset_csv_path = os.path.join(data_base_path, csv_out_name)

## ----------------------------------------

arch_json_name = "architecture.json"
arch_json_path = os.path.join(model_base_path, arch_json_name)

weights_name = "weights.h5"
weights_path = os.path.join(model_base_path, weights_name)

## ----------------------------------------

"""
 N.B. the warnings in the output are due to the fact that the model was developed for
 Keras 1, and the config file has been converted in a Keras-2-compatible file

 Keras 2 uses different naming conventions/def.s, so in order to get rid of
 all the warnings one should change all the layers def.s in the JSON file
"""

# load the model architecture from the config file, then load the model weights 
with open(arch_json_path, 'r') as json_file:
  model_json = json.load(json_file)  

model = keras.models.model_from_config(model_json)
model.summary()

model.load_weights(weights_path)

## ----------------------------------------

# define a new dataframe to store basics information + baseline output
# as well as the reproduced experiment output
df_keys = ['PatientID', 'StudyInstanceUID', 'SeriesInstanceUID_CT',
           'SeriesInstanceUID_RTSTRUCT', 'CNN_output_raw', 'CNN_output_argmax',
           'baseline_output_raw', 'baseline_output_argmax', 'surv2yr'
           ]

data = {k : list() for k in df_keys}

# analysis results
res_df = pd.DataFrame(data, dtype = object)
res_csv_name = 'res.csv'
res_csv_path = os.path.join(output_base_path, res_csv_name)

# analysis baseline: Hosny et Al. results
baseline_csv_name = 'nsclc-radiomics_hosny_baseline.csv'
baseline_csv_path = os.path.join(data_base_path, baseline_csv_name)
baseline_df = pd.read_csv(baseline_csv_path)

## ----------------------------------------

y_pred_dict = dict()

input_df = pd.read_csv(dataset_csv_path)
input_df = input_df[~input_df["crop_shape"].isna()]

input_subj_list = list(input_df["PatientID"])

for idx, subj in enumerate(input_subj_list):

  print("Processing subject '%s' (%d/%d)... "%(subj, idx + 1, len(input_subj_list)), end = '\r')

  """
  The NRRD files for each subject in "input_df" should exist and readable
  (already double checked during the creation of 'lung1_proc_details.csv').
  If not, just run the code in  'lung1_det_csv.ipynb', found under /src.
  """
  
  subj_df = input_df[input_df['PatientID'] == subj]
  
  ct_res_crop_path = os.path.join(preproc_data_path, subj, subj + '_ct_res_crop.nrrd')
  
  input_vol = get_input_volume(input_ct_nrrd_path = ct_res_crop_path)
  input_vol = np.expand_dims(input_vol, axis = 0)
  input_vol = np.expand_dims(input_vol, axis = -1)
  
  y_pred_raw = model.predict(input_vol)
  y_pred_argmax = int(np.argmax(y_pred_raw[0]))
  
  subj_dict = dict()
  subj_dict["PatientID"] = subj
  
  subj_dict["StudyInstanceUID"] = subj_df["ctStudyInstanceUID"].values[0]
  subj_dict["SeriesInstanceUID_CT"] = subj_df["ctSeriesInstanceUID"].values[0]
  subj_dict["SeriesInstanceUID_RTSTRUCT"] = subj_df["rtstructSeriesInstanceUID"].values[0]

  subj_dict["CNN_output_raw"] = y_pred_raw.tolist()[0]
  subj_dict["CNN_output_argmax"] = y_pred_argmax
  
  baseline_output_list = list()
  
  try:
    baseline_output_list.append(baseline_df[baseline_df["id"] == ' %s'%(subj)]["logit_0"].values[0])
    baseline_output_list.append(baseline_df[baseline_df["id"] == ' %s'%(subj)]["logit_1"].values[0])

    #subj_dict['baseline_output_raw'] = np.array(baseline_output_list)
    subj_dict['baseline_output_raw'] = baseline_output_list
    subj_dict['baseline_output_argmax'] = int(np.argmax(np.array(baseline_output_list)))
    
    subj_dict['surv2yr'] = baseline_df[baseline_df["id"] == ' %s'%(subj)]["surv2yr"].values[0]
  except:
    pass

  res_df = res_df.append(subj_dict, ignore_index = True)

res_df.to_csv(res_csv_path, index = False)