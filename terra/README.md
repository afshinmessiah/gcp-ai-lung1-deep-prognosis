# Terra Docker Testing

Once in the `terra` directory, run the following to build the container (fetch `tensorflow/tensorflow:1.15.4-gpu-py3`, install Plastimatch and the python requirements except for Tensorflow, already installed):
```
sudo docker build -t tfcpu_custom .
```

By default, the entry point to the container is set to `/bin/bash`, so running the command below will spawn a bash session inside the container:
```
sudo docker run -it --rm --name test tfcpu_custom
```

From this point, as all the code and data in `gcp-ai-lung1-deep-prognosis` are copied in the container under `/home/terra-test/terra/` during the creation of the latter, to test the pipeline on `LUNG1-001` and `LUNG2-002` run:

```
cd /home/terra-test/terra/
````

```
./run_pipeline.sh
````

The results - the resampled and cropped-around-the-center-of-mass NRRD files (CT and GTV-1 RTSTRUCT), a couple of JSON files storing processing information, some QA images and a CSV file storing the result of the inference phase as well as `PatientID`, `ctStudyInstanceUID`, `ctSeriesInstanceUID`, and `rtstructSeriesInstanceUID` associated to the patient - are stored by default under:
```
/home/terra-test/data/nsclc-radiomics_preprocessed_pat/
```
