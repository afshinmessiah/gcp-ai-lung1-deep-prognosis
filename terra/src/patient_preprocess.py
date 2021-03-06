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
import argparse

import pandas as pd
import SimpleITK as sitk

from my_lib.utils import *
from my_lib.data_utils import *

  
## ----------------------------------------
def patient_preprocess(patient_id: str,
                       res_dir_path: str,
                       ):
    # location where the tmp nrrd files (resampled CT/RTSTRUCT nrrd) should be saved
    # by the "export_res_nrrd_from_dicom" function found in preprocess.py
    ct_nrrd_path = os.path.join(res_dir_path, patient_id + '_ct_resampled.nrrd')
    rt_nrrd_path = os.path.join(res_dir_path, patient_id + '_rt_resampled.nrrd')

    # location where the nrrd files (cropped resampled CT/RTSTRUCT nrrd) should be saved
    # by the "export_com_subvolume" function found in preprocess.py
    ct_nrrd_crop_path = os.path.join(res_dir_path, patient_id + '_ct_res_crop.nrrd')
    rt_nrrd_crop_path = os.path.join(res_dir_path, patient_id + '_rt_res_crop.nrrd')
    # sanity check
    assert(os.path.exists(ct_nrrd_path))
    assert(os.path.exists(rt_nrrd_path))
    sitk_vol = sitk.ReadImage(ct_nrrd_path)
    vol = sitk.GetArrayFromImage(sitk_vol)

    
    sitk_seg = sitk.ReadImage(rt_nrrd_path)
    seg = sitk.GetArrayFromImage(sitk_seg)



    com = compute_center_of_mass(seg)
    com_int = [int(coord) for coord in com]
    whole_ct_png_path = os.path.join(res_dir_path, 'qa_' + patient_id + '_whole_ct_com.png')
    crop_ct_png_path = os.path.join(res_dir_path, 'qa_' + patient_id + '_crop_ct_com.png')
    ## ----------------------------------------
    
    # export the CoM slice (CT + RTSTRUCT) for quality control
    export_png_slice(input_volume=vol,
                    input_segmask=seg,
                    fig_out_path=whole_ct_png_path,
                    fig_dpi=220,
                    lon_slice_idx=com_int[0],
                    cor_slice_idx=com_int[1],
                    sag_slice_idx=com_int[2],
                    z_first=True)

    try:
        # crop a (150, 150, 150) subvolume from the resampled scans, get rid of the latter
        proc_log = export_com_subvolume(ct_nrrd_path=ct_nrrd_path, 
                                        rt_nrrd_path=rt_nrrd_path, 
                                        crop_size=(150, 150, 150), 
                                        output_dir=res_dir_path,
                                        pat_id=patient_id,
                                        z_first=True, 
                                        rm_orig=True)
    except Exception as e:
        print(e)
        sys.exit(-1)

    # log CoM information
    
    com_log_path = os.path.join(res_dir_path, patient_id + '_com_log.json')
    com_log_dict = {k : v for (k, v) in proc_log.items() if "com_int" in k}
    
    with open(com_log_path, 'w') as json_file:
        json.dump(com_log_dict, json_file, indent=2)
    
    # if CoM calculation goes wrong then continue
    proc_log_crop = {k : v for (k, v) in proc_log.items() if "cropping" in k}
    if len(proc_log_crop) == 0:
        os.remove(ct_nrrd_path)
        os.remove(rt_nrrd_path)
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
    export_png_slice(input_volume=vol_crop,
                    input_segmask=seg_crop,
                    fig_out_path=crop_ct_png_path,
                    fig_dpi=220,
                    lon_slice_idx=75,
                    cor_slice_idx=75,
                    sag_slice_idx=75,
                    z_first=True)