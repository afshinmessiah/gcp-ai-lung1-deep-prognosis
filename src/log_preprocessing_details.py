"""
    ----------------------------------------
    IDC MedIA use case (GCP Demo)
    
    data preprocessing details logging
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    Modified: 02 DEC 20
    ----------------------------------------
    
"""

import os
import sys
import json
import pydicom
import numpy as np
import pandas as pd
import SimpleITK as sitk


## ----------------------------------------

data_base_path = '../data'

dataset_name = 'nsclc-radiomics'
dataset_path = os.path.join(data_base_path, dataset_name)
data_path = os.path.join(dataset_path, 'dicom')

preproc_dataset_name = dataset_name + '_preprocessed'
preproc_dataset_path = os.path.join(data_base_path, preproc_dataset_name)
preproc_data_path = os.path.join(preproc_dataset_path, 'nrrd')

## ----------------------------------------

csv_out_name = 'nsclc-radiomics_preproc_details.csv'
dataset_csv_path = os.path.join(data_base_path, csv_out_name)


df_keys = ['PatientID',
           'path_to_ct_dir', 'ctStudyInstanceUID', 'ctSeriesInstanceUID',
           'path_to_rt_dir', 'rtstructStudyInstanceUID', 'rtstructSeriesInstanceUID',
           'path_to_seg_dir', 'segStudyInstanceUID', 'segSeriesInstanceUID',
           'rt_exported', 'orig_shape', '1mm_iso_shape', 'crop_shape', 'com_int', 'bbox']

data = {k : list() for k in df_keys}

det_df = pd.DataFrame(data = data, dtype = object)

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

pat_to_exclude = list()

pat_list = sorted(list(set(pat_list) - set(pat_to_exclude)))


for pat_num, pat in enumerate(pat_list):

  print("\rProcessing patient '%s' (%d/%d)... "%(pat, pat_num + 1,
                                                 len(pat_list)),
        end = '')
    
  pat_df = cohort_df[cohort_df['PatientID'] == pat]
            
  # init a dictionary with the same keys as "df_keys" to populate the latter
  pat_dict = dict()
  pat_dict["PatientID"] = pat

  pat_dir_path = os.path.join(preproc_data_path, pat)
  pat_json_path = os.path.join(pat_dir_path, pat + '_lookup_info.json')

  with open(pat_json_path, 'r') as json_file:
    lookup_dict = json.load(json_file)
    
  pat_dict["path_to_ct_dir"] = lookup_dict[pat]["path_to_ct_dir"]
  pat_dict["ctStudyInstanceUID"] = pat_df['ctStudyInstanceUID'].values[0]
  pat_dict["ctSeriesInstanceUID"] = pat_df['ctSeriesInstanceUID'].values[0]

  pat_dict["path_to_rt_dir"] = lookup_dict[pat]["path_to_rt_dir"]
  pat_dict["rtstructStudyInstanceUID"] = pat_df['rtstructStudyInstanceUID'].values[0]
  pat_dict["rtstructSeriesInstanceUID"] = pat_df['rtstructSeriesInstanceUID'].values[0]

  pat_dict["path_to_seg_dir"] = lookup_dict[pat]["path_to_seg_dir"]
  pat_dict["segStudyInstanceUID"] = pat_df['segStudyInstanceUID'].values[0]
  pat_dict["segSeriesInstanceUID"] = pat_df['segSeriesInstanceUID'].values[0]
    
  # ----------------------------------------
    
  # populate the "rt_exported" field
  rt_folder = os.path.join(pat_dir_path, pat  + '_whole_ct_rt')
  pat_dict['rt_exported'] = [f for f in os.listdir(rt_folder) if 'gtv-1' in f.lower()][0].split('.nrrd')[0]   
  if pat_dict['rt_exported'] != 'GTV-1':
    a.append(pat)
    
  # ----------------------------------------
    
  dicom_ct_path = lookup_dict[pat]["path_to_ct_dir"]
    
  dcm_file_path = os.path.join(dicom_ct_path,                 # parent folder
                               os.listdir(dicom_ct_path)[0])  # *.dcm files

  dcm_file = pydicom.dcmread(dcm_file_path)
  n_dcm_files = len([f for f in os.listdir(dicom_ct_path) if '.dcm' in f])

  xy = int(float(dcm_file.Rows)*float(dcm_file.PixelSpacing[0]))
  
  # FIXME: is this the best way to do it?
  z = int(float(dcm_file.SliceThickness)*float(n_dcm_files))
    
  orig_dcm_shape = (n_dcm_files, dcm_file.Columns, dcm_file.Rows)
  res_dcm_shape = (z, xy, xy)
    
  pat_dict['orig_shape'] = orig_dcm_shape
  pat_dict['1mm_iso_shape'] = res_dcm_shape
    
  # ----------------------------------------
     
  com_json_path = os.path.join(pat_dir_path, pat + '_com_log.json')
    
  try:
    with open(com_json_path, 'r') as json_file:
      com_dict = json.load(json_file)
      pat_dict['com_int'] = tuple(com_dict["com_int"])
  except:
    print('_com_log.json loading error;')
    
  # ----------------------------------------
    
  bbox_json_path = os.path.join(pat_dir_path, pat + '_crop_log.json')
    
  try:
    with open(bbox_json_path, 'r') as json_file:
      bbox_dict = json.load(json_file)
      pat_dict['bbox'] = bbox_dict
  except:
    print('_crop_log.json loading error;')
    
  # ----------------------------------------
  ct_res_crop_path = os.path.join(pat_dir_path, pat + '_ct_res_crop.nrrd')
    
  try:
    sitk_ct_res_crop = sitk.ReadImage(ct_res_crop_path)
    pat_dict['crop_shape'] = sitk_ct_res_crop.GetSize()
  except:
    print('_ct_res_crop.nrrd loading error;')
        
  # ----------------------------------------
    
  det_df = det_df.append(pat_dict, ignore_index = True)

det_df.to_csv(dataset_csv_path, index = False)