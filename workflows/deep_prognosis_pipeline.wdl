version 1.0
import "tasks/input_preparations.wdl" as sub_
workflow deep_prognosis_workflow {
    input {
        Array[String] patient_id
        Array[String] ct_seriesinstanceuid
        Array[String] rt_seriesinstanceuid
        Array[String] sg_seriesinstanceuid
        String dest_bucket_name
    }
    String json_file = 'queried_inputs.json'
    call sub_.QueryInputs as external_q_inputs{
        input: patient_id=patient_id,
        ct_seriesinstanceuid=ct_seriesinstanceuid,
        rt_seriesinstanceuid=rt_seriesinstanceuid,
        sg_seriesinstanceuid=sg_seriesinstanceuid,
        json_file=json_file
    }
    # output{
    #     Array[String] out = QueryInputs.out
    #     Array[File] jsonfile = QueryInputs.json

    # }


    scatter(j in range(length(external_q_inputs.json)))
    {
        Object tmp = read_json(external_q_inputs.json[j])
        Array[Object] inputs = tmp.data
    }
    Array[Object] flattened_inputs = flatten(inputs)
    
    scatter (i in range(length(flattened_inputs)))
    {
        String pid = flattened_inputs[i].PATIENTID
        String src_bukcet = flattened_inputs[i].GCS_BUCKET
        call deep_prognosis_task
        { 
            input: dicom_ct_list=flattened_inputs[i].INPUT_CT,
            dicom_rt_list=flattened_inputs[i].INPUT_RT,
            output_dir="./Output/" + src_bukcet + "/" + pid,
            pat_id=pid,
            dest_bucket_name=dest_bucket_name
        }
        Object OutputSt = { 
            "Patient_id": pid,
            "ctSeriesInstanceUID":flattened_inputs[i].CTSERIESINSTANCEUID,
            "rtstructSeriesInstanceUID":flattened_inputs[i].RTSTRUCTSERIESINSTANCEUID,
            "prob_logit_0": deep_prognosis_task.out_.prob_logit_0,
            "prob_logit_1": deep_prognosis_task.out_.prob_logit_1,
            "output": deep_prognosis_task.out_.destination,
        } 

    }
   
    output {
        Array[Object] wf_output =  OutputSt
        # Array[File] w_output1 = flatten(deep_prognosis_task.files_1)
        # Array[File] w_output2 = flatten(deep_prognosis_task.files_2)
        # File jj = jjjjsss
        # File inn = innnppp
    }
    meta {
    allowNestedInputs: true
    }
}
task deep_prognosis_task
{
    input { 
        Array[File] dicom_ct_list
        Array[File] dicom_rt_list
        String output_dir
        String pat_id
        String dest_bucket_name
    }
    String dest_bucket_path = 'gs://' + dest_bucket_name
    String ct_interpolation = 'linear'
    String output_dtype = "int"
    Float prob_logit_0 = 0.0
    Float prob_logit_1 = 0.0
    command
    <<<
        python3 <<CODE
        import sys
        sys.path.insert(1, '/deep-prognosis-code/terra/src')
        import os
        import subprocess
        import json
        from patient_convert import patient_convert
        from patient_preprocess import patient_preprocess
        from patient_inference import patient_inference

        dicom_ct_path = os.path.dirname('~{dicom_ct_list[0]}')
        print('dicom_ct_path = {}'.format(dicom_ct_path))
        dicom_rt_path = '~{dicom_rt_list[0]}'
        print('dicom_rt_path = {}'.format(dicom_rt_path))
        destination_bucket_name = '~{dest_bucket_path}'
        patient_id = '~{pat_id}'
        output_dir = os.path.abspath('~{output_dir}')
        print('out dir abs is ', output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        network_architect_json_path = '/deep-prognosis-code/terra/models/architecture.json'
        network_weights_path = '/deep-prognosis-code/terra/models/weights.h5'
        patient_convert(dicom_ct_path, dicom_rt_path, output_dir,patient_id)
        patient_preprocess(patient_id, output_dir)
        inference = patient_inference(
            network_architect_json_path,
            network_weights_path,
            output_dir,
            patient_id)
        level1 = os.path.basename(output_dir)
        level2 = os.path.basename(os.path.dirname(output_dir))
        dest2 = os.path.join(destination_bucket_name, level2) 
        dest1 = os.path.join(dest2, level1) 

        inference['destination'] = dest1 
        filename = 'output.json'
        with open(filename, 'w') as fp:
            json.dump(inference, fp, indent=4)
        CODE
        gsutil cp -r '~{output_dir}/..' '~{dest_bucket_path}'
        
    >>>
    runtime {
        # docker: "biocontainers/plastimatch:v1.7.4dfsg.1-2-deb_cv1"
        docker: "afshinmha/deep-prognosis:lungs"
        memory: "8GB"

    }
    output {
        Object out_ = read_json("output.json")
    }
    meta {
        author: "Afshin"
        email: "akbarzadehm@gmail.com"
        description: "deep prognosis pipeline task."
    }
    


}
