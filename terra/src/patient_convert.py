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
import argparse

import pandas as pd
import SimpleITK as sitk

from my_lib.utils import *
from my_lib.data_utils import *

def patient_convert(dicom_ct_path: str, 
                    dicom_rt_path: str, 
                    output_dir: str,
                    patient_id: str
                    ):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # location where the tmp nrrd files (resampled CT/RTSTRUCT nrrd) should be saved
    # by the "export_res_nrrd_from_dicom" function found in preprocess.py
    res_ct_nrrd_path = os.path.join(
        output_dir, patient_id + '_ct_resampled.nrrd')
    res_rt_nrrd_path = os.path.join(
        output_dir, patient_id + '_rt_resampled.nrrd')
    
    # sanity check
    assert os.path.exists(dicom_ct_path)
    assert os.path.exists(dicom_rt_path)
        
    ## ----------------------------------------
    
    try:
        proc_log = export_res_nrrd_from_dicom(dicom_ct_path=dicom_ct_path, 
                                            dicom_rt_path=dicom_rt_path, 
                                            output_dir=output_dir,
                                            ct_interpolation = 'linear',
                                            pat_id = patient_id,
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