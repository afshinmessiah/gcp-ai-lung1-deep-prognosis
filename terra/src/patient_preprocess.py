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
  
## ----------------------------------------

# sanity check
assert(os.path.exists(res_ct_nrrd_path))
assert(os.path.exists(res_rt_nrrd_path))
  
sitk_vol = sitk.ReadImage(res_ct_nrrd_path)
vol = sitk.GetArrayFromImage(sitk_vol)
  
sitk_seg = sitk.ReadImage(res_rt_nrrd_path)
seg = sitk.GetArrayFromImage(sitk_seg)


com = compute_center_of_mass(seg)
com_int = [int(coord) for coord in com]

# export the CoM slice (CT + RTSTRUCT) for quality control
export_png_slice(input_volume = vol,
                 input_segmask = seg,
                 fig_out_path = os.path.join(res_pat_dir_path, 'qa_' + pat + '_whole_ct_com.png'),
                 fig_dpi = 220,
                 lon_slice_idx = com_int[0],
                 cor_slice_idx = com_int[1],
                 sag_slice_idx = com_int[2],
                 z_first = True)

try:
  # crop a (150, 150, 150) subvolume from the resampled scans, get rid of the latter
  proc_log = export_com_subvolume(ct_nrrd_path = res_ct_nrrd_path, 
                                  rt_nrrd_path = res_rt_nrrd_path, 
                                  crop_size = (150, 150, 150), 
                                  output_dir = res_pat_dir_path,
                                  pat_id = pat,
                                  z_first = True, 
                                  rm_orig = True)
except Exception as e:
  print(e)
  sys.exit(-1)

# log CoM information
com_log_path = os.path.join(res_pat_dir_path, pat + '_com_log.json')
com_log_dict = {k : v for (k, v) in proc_log.items() if "com_int" in k}
  
with open(com_log_path, 'w') as json_file:
  json.dump(com_log_dict, json_file, indent = 2)
  
# if CoM calculation goes wrong then continue
proc_log_crop = {k : v for (k, v) in proc_log.items() if "cropping" in k}
if len(proc_log_crop) == 0:
  os.remove(res_ct_nrrd_path)
  os.remove(res_rt_nrrd_path)
  sys.exit(-1)
  
# check the cropped volumes have been exported as intended
assert(np.sum(np.array(list(proc_log_crop.values()))) == 0)
assert(os.path.exists(ct_nrrd_crop_path))
assert(os.path.exists(rt_nrrd_crop_path))
  
sitk_vol = sitk.ReadImage(ct_nrrd_crop_path)
vol_crop = sitk.GetArrayFromImage(sitk_vol)

sitk_seg = sitk.ReadImage(rt_nrrd_crop_path)
seg_crop = sitk.GetArrayFromImage(sitk_seg)
  
# export the cropped subvolume CoM slice (CT + RTSTRUCT) for quality control
export_png_slice(input_volume = vol_crop,
                 input_segmask = seg_crop,
                 fig_out_path = os.path.join(res_pat_dir_path, 'qa_' + pat + '_crop_ct_com.png'),
                 fig_dpi = 220,
                 lon_slice_idx = 75,
                 cor_slice_idx = 75,
                 sag_slice_idx = 75,
                 z_first = True)