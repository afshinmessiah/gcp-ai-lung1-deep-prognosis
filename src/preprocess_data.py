"""
    ----------------------------------------
    IDC MedIA use case (GCP Demo)
    
    data preprocessing
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
import numpy as np
import pandas as pd
import SimpleITK as sitk

from my_lib.utils import *
from my_lib.data_utils import *

## ----------------------------------------

data_base_path = '../data'

dataset_name = 'nsclc-radiomics'
dataset_path = os.path.join(data_base_path, dataset_name)
data_path = os.path.join(dataset_path, 'dicom')

preproc_dataset_name = dataset_name + '_preprocessed'
preproc_dataset_path = os.path.join(data_base_path, preproc_dataset_name)
preproc_data_path = os.path.join(preproc_dataset_path, 'nrrd')

if not os.path.exists(preproc_data_path):
    os.makedirs(preproc_data_path)

## ----------------------------------------

cohort_table_name = 'nsclc-radiomics_table.csv'
cohort_table_path = os.path.join(data_base_path, cohort_table_name)
cohort_df = pd.read_csv(cohort_table_path)
pat_list = cohort_df.PatientID.values

# FIXME: patients which are found to be problematic should be exluded
# try-except is the best fix, but for the time being put them here?
# note: try-except sometimes doesn't help - as some patients make SITK crash (memory leak)
pat_to_exclude = ['LUNG1-021',
                  'LUNG1-058',
                  'LUNG1-085',
                  'LUNG1-104']

#pat_to_exclude = list()

pat_list = sorted(list(set(pat_list) - set(pat_to_exclude)))

## ----------------------------------------

for pat_num, pat in enumerate(pat_list):
    
  print("\nPatient %d/%d (%s)"%(pat_num + 1, len(cohort_df), pat))
    
  pat_dir_path = os.path.join(preproc_data_path, pat)
    
  if not os.path.exists(pat_dir_path):
    os.mkdir(pat_dir_path)
    
  # location where the tmp nrrd files (resampled CT/RTSTRUCT nrrd) should be saved
  # by the "export_res_nrrd_from_dicom" function found in preprocess.py
  ct_nrrd_path = os.path.join(pat_dir_path, pat + '_ct_resampled.nrrd')
  rt_nrrd_path = os.path.join(pat_dir_path, pat + '_rt_resampled.nrrd')

  # location where the nrrd files (cropped resampled CT/RTSTRUCT nrrd) should be saved
  # by the "export_com_subvolume" function found in preprocess.py
  ct_nrrd_crop_path = os.path.join(pat_dir_path, pat + '_ct_res_crop.nrrd')
  rt_nrrd_crop_path = os.path.join(pat_dir_path, pat + '_rt_res_crop.nrrd')
    
  # if the latter are already there, skip the processing
  if os.path.exists(ct_nrrd_crop_path) and os.path.exists(rt_nrrd_crop_path):
    print("%s\nand\n%s\nfound, skipping the processing for patient %s..."%(ct_nrrd_crop_path,
                                                                           rt_nrrd_crop_path, 
                                                                           pat))
    continue
    
    ## ----------------------------------------
    
  pat_df = cohort_df[cohort_df["PatientID"] == pat]

  path_to_ct_dir = os.path.join(data_path,
                                pat_df["ctStudyInstanceUID"].values[0],
                                pat_df["ctSeriesInstanceUID"].values[0])

  path_to_rt_dir = os.path.join(data_path,
                                pat_df["rtstructStudyInstanceUID"].values[0],
                                pat_df["rtstructSeriesInstanceUID"].values[0])

  path_to_seg_dir = os.path.join(data_path, 
                                 pat_df["segStudyInstanceUID"].values[0], 
                                 pat_df["segSeriesInstanceUID"].values[0])

  # sanity check
  assert os.path.exists(path_to_ct_dir)
  assert os.path.exists(path_to_rt_dir)
  assert os.path.exists(path_to_seg_dir)    
    
  # log lookup informations (human-readable to StudyUID and SeriesUID)
  lookup_dict_path = os.path.join(pat_dir_path, pat + '_lookup_info.json')
    
  lookup_dict = dict()
  lookup_dict[pat] = dict()
    
  lookup_dict[pat]["path_to_ct_dir"] = path_to_ct_dir
  lookup_dict[pat]["ctStudyInstanceUID"] = pat_df["ctStudyInstanceUID"].values[0]
  lookup_dict[pat]["ctSeriesInstanceUID"] = pat_df["ctSeriesInstanceUID"].values[0]
    
  lookup_dict[pat]["path_to_rt_dir"] = path_to_rt_dir
  lookup_dict[pat]["rtstructStudyInstanceUID"] = pat_df["rtstructStudyInstanceUID"].values[0]
  lookup_dict[pat]["rtstructSeriesInstanceUID"] = pat_df["rtstructSeriesInstanceUID"].values[0]
    
  lookup_dict[pat]["path_to_seg_dir"] = path_to_seg_dir
  lookup_dict[pat]["segStudyInstanceUID"] = pat_df["segStudyInstanceUID"].values[0]
  lookup_dict[pat]["segSeriesInstanceUID"] = pat_df["segSeriesInstanceUID"].values[0]
    
  with open(lookup_dict_path, 'w') as json_file:
    json.dump(lookup_dict, json_file, indent = 2)
    
  ## ----------------------------------------
    
  try:
    proc_log = export_res_nrrd_from_dicom(dicom_ct_path = path_to_ct_dir, 
                                          dicom_rt_path = path_to_rt_dir, 
                                          output_dir = pat_dir_path,
                                          ct_interpolation = 'linear',
                                          pat_id = pat,
                                          output_dtype = "float")
    
  except Exception as e:
    print(e)
    continue
    
  # check every step of the DICOM to NRRD conversion returned 0 (everything's ok)
  assert(np.sum(np.array(list(proc_log.values()))) == 0)
    
  # sanity check
  assert(os.path.exists(ct_nrrd_path))
  assert(os.path.exists(rt_nrrd_path))
    
  sitk_vol = sitk.ReadImage(ct_nrrd_path)
  vol = sitk.GetArrayFromImage(sitk_vol)
    
  sitk_seg = sitk.ReadImage(rt_nrrd_path)
  seg = sitk.GetArrayFromImage(sitk_seg)
    
  # sanity check
  assert(vol.shape == seg.shape)
    
  com = compute_center_of_mass(seg)
  com_int = [int(coord) for coord in com]

  # export the CoM slice (CT + RTSTRUCT) for quality control
  export_png_slice(input_volume = vol,
                   input_segmask = seg,
                   fig_out_path = os.path.join(pat_dir_path, pat + '_whole_CT_CoM.png'),
                   fig_dpi = 220,
                   lon_slice_idx = com_int[0],
                   cor_slice_idx = com_int[1],
                   sag_slice_idx = com_int[2],
                   z_first = True)
  
  try:
    # crop a (150, 150, 150) subvolume from the resampled scans, get rid of the latter
    proc_log = export_com_subvolume(ct_nrrd_path = ct_nrrd_path, 
                                    rt_nrrd_path = rt_nrrd_path, 
                                    crop_size = (150, 150, 150), 
                                    output_dir = pat_dir_path,
                                    pat_id = pat,
                                    z_first = True, 
                                    rm_orig = True)
  except Exception as e:
    print(e)
    continue
  
  # log CoM information
  com_log_path = os.path.join(pat_dir_path, pat + '_com_log.json')
  com_log_dict = {k : v for (k, v) in proc_log.items() if "com_int" in k}
    
  with open(com_log_path, 'w') as json_file:
    json.dump(com_log_dict, json_file, indent = 2)
    
  # if CoM calculation goes wrong then continue
  proc_log_crop = {k : v for (k, v) in proc_log.items() if "cropping" in k}
  if len(proc_log_crop) == 0:
    os.remove(ct_nrrd_path)
    os.remove(rt_nrrd_path)
    continue
    
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
                   fig_out_path = os.path.join(pat_dir_path, pat + '_crop_CT_CoM.png'),
                   fig_dpi = 220,
                   lon_slice_idx = 75,
                   cor_slice_idx = 75,
                   sag_slice_idx = 75,
                   z_first = True)
    
  print("\n----------------------------------------\n")