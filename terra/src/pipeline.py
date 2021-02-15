from patient_convert import patient_convert
from patient_preprocess import patient_preprocess
from patient_inference import patient_inference

dicom_ct_path = 
dicom_rt_path =
source_bucket_name =
patient_id =
output_dir = 
ct_nrrd_path = os.path.join(output_dir, patient_id + '_ct_resampled.nrrd')
rt_nrrd_path = os.path.join(output_dir, patient_id + '_rt_resampled.nrrd')
ct_nrrd_crop_path = os.path.join(res_pat_dir_path, pat + '_ct_res_crop.nrrd')
rt_nrrd_crop_path = os.path.join(res_pat_dir_path, pat + '_rt_res_crop.nrrd')
network_architect_json_path = 'models/architecture.json'
network_weights_path = 'models/wights.h5'
patient_convert(dicom_ct_path, dicom_rt_path, output_dir,patient_id)
patient_preprocess(ct_nrrd_path,rt_nrrd_path,ct_nrrd_crop_path,rt_nrrd_crop_path)
inference = patient_inference(network_architect_json_path,network_weights_path,preprocessed_output_path,patient_identity)
