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
    # File jjjjsss = write_object(tmp)
    # Array[Object] inputs = tmp.data
    # File innnppp = write_objects(inputs)
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

    }
   
    output {
        Array[String] dest = deep_prognosis_task.destination
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
    command
    <<<
        pwd
        ls -al
        cd ~
        ls -al
        cat "/deep-prognosis-code/terra/src/patient_preprocess.py"
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
        # export_res_nrrd_from_dicom(
        #     dicom_ct_path,
        #     dicom_rt_path,
        #     '~{output_dir}', '~{pat_id}',
        #     '~{ct_interpolation}', '~{output_dtype}'
        # )
        # output_file_list = Find('~{output_dir}')
        # with open('outputfiles.json', 'w') as fp:
        #     json.dump({'data':output_file_list}, fp, indent=4)
        # print('this is all {} files\n {}'.format(
        #     len(output_file_list), json.dumps(output_file_list, indent=4)))
        # out_text = ''
        # for f in output_file_list:
        #     out_text +='{}\n'.format(f)
        # text_file = open('outputfiles.txt', "w")
        # text_file.write(out_text)
        # text_file.close()
        CODE
        gsutil cp -r '~{output_dir}' '~{dest_bucket_path}'
    >>>
    runtime {
        # docker: "biocontainers/plastimatch:v1.7.4dfsg.1-2-deb_cv1"
        docker: "afshinmha/deep-prognosis:lungs"
        memory: "8GB"

    }
    output {
        String destination = dest_bucket_path + "/" + output_dir
        # Object outtt = read_json('outputfiles.json')
        # Array[File] outputfiles = outtt.data
        # Array[File] all_files = read_lines('outputfiles.txt')
        # Array[File] files_1 = glob(output_dir + "/*")
        # Array[File] files_2 = glob(output_dir + "/*/*")
    }
    meta {
        author: "Afshin"
        email: "akbarzadehm@gmail.com"
        description: "deep prognosis pipeline task."
    }
    


}
