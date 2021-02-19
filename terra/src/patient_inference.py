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
import json
import argparse

import keras
import numpy as np
import pandas as pd

from my_lib.utils import *
from my_lib.data_utils import *



## ----------------------------------------
def patient_inference(network_architect_json_path: str,
                      network_weights_path: str,
                      preprocessed_output_path: str,
                      patient_identity: str) -> dict:
    """
        N.B. the warnings in the output are due to the fact that the model was developed for
        Keras 1, and the config file has been converted in a Keras-2-compatible file

        Keras 2 uses different naming conventions/def.s, so in order to get rid of
        all the warnings one should change all the layers def.s in the JSON file
    """
    patient_preproc_folder = os.path.basename(preprocessed_output_path)
    # load the model architecture from the config file, then load the model weights 
    with open(network_architect_json_path, 'r') as json_file:
        model_json = json.load(json_file)  

    model = keras.models.model_from_config(model_json)
    model.load_weights(network_weights_path)

    ## ----------------------------------------

    # define a new dataframe to store basics information + baseline output
    # as well as the reproduced experiment output
    # df_keys = ['PatientID', 'ctStudyInstanceUID', 'ctSeriesInstanceUID',
    #         'rtstructSeriesInstanceUID', 'prob_logit_0', 'prob_logit_0']

    # # data = {k : list() for k in df_keys}

    # # analysis results
    # res_df = pd.DataFrame(data, dtype = object)
    # res_csv_name = 'inference_res_' + patient_preproc_folder + '.csv'
    # res_csv_path = os.path.join(preprocessed_output_path, res_csv_name)

    ## ----------------------------------------

    ct_res_crop_path = os.path.join(
        preprocessed_output_path, patient_identity + '_ct_res_crop.nrrd')

    input_vol = get_input_volume(input_ct_nrrd_path = ct_res_crop_path)
    input_vol = np.expand_dims(input_vol, axis = 0)
    input_vol = np.expand_dims(input_vol, axis = -1)

    y_pred_raw = model.predict(input_vol)


    pat_dict = {}
    pat_dict["prob_logit_0"] = y_pred_raw.tolist()[0][0]
    pat_dict["prob_logit_1"] = y_pred_raw.tolist()[0][1]
    return pat_dict