# `data` subdir

The csv file `lung1_mapping.csv` stores the output of `utils.create_lung1_idmap()`.

The csv file `lung1_proc_details.csv` stores each and every LUNG1 volume details:
* a mapping between the human-readable name, `StudyInstanceUID`, and CT/RTSTRUCT `SeriesInstanceUID` (redundant, found also in `lung1_mapping.csv`);
* a record `rt_exported` of the structures exported (from RTSTRUCT) by plastimatch;
* information regarding the dimensions of the original volume, its resampled 1mm isotropic version, and the cropped one;
* both the center of mass (CoM) and the bounding box used to go from the 1mm isotropic version of each volume to its cropped one.
Furthermore, the csv file is filled with NaN where the information is missing (e.g., the RTSTRUCT DICOM is not available and thus the majority of the steps are not executed).

The json file `lung1_missing.json` stores details on the missing sequences (only the volumes for which some sequence is missing are listed).

## The `lung1_preprocessed` Folder

The folder is structured as follows:
```
lung1_preprocessed
                  |
                   nrrd
                       |_LUNG1-001
                       |          |_"001_ct_res_crop.nrrd"
                       |          |_"001_rt_res_crop.nrrd"
                       |          |_"001_crop_log.json"
                       |          |_"001_rt_list.txt"
                       |          |_"001_lookup_info.json"
                       |          |_"001_whole_ct_com.png"
                       |          |_"001_crop_ct_com.png"
                       |
                       |_LUNG1-002
                       |          |_"002_ct_res_crop.nrrd"
                       |          |_ ...
                      ...        ...

```

Where:
* `ct_res_crop.nrrd` contains the DICOM CT sequence resampled and cropped (150x150x150);
* `rt_res_crop.nrrd` contains the DICOM RTSTRUCT sequence resampled and cropped (150x150x150);
* `crop_log.json` stores the bbox wrt which the crop has been computed starting from the `*_resampled.nrrd` files (that could very well be not present anymore in the directory - for lack of storage reasons - but are computed exploiting the `preprocess.export_res_nrrd_from_dicom()` and then calling `preprocess.export_com_subvolume()` with `rm_orig = False` in the dataset preprocessing notebook/script);
* `com_log.json` stores the CoM, i.e., the coordinate around which the cropping of a subvolume of size logged in `crop_log.json` is computed. Please note that this is not redundant - in the case a "uniform" crop is not possible (i.e., the 150x150x150 subvolume centered around CoM falls partially outside the resampled CT) the CoM information would be lost otherwise;
* `rt_list.txt` stores the name of the label exported by `plastimatch` in the DICOM RTSTRUCT to nrrd step (should be "GTV-1");
* `lookup_info.json` stores lookup information that should be found also in the `lung1_mapping.csv` file (i.e., how to map the human-readable name `LUNG1-XXX` to the `StudyInstanceUID`, the `SeriesInstanceUID` ...).
* `whole_ct_com.png` stores the three main views of the whole CT scan after nrrd conversion and resampling (CoM slices);
* `crop_ct_com.png` stores the three main views of the cropped CT scan (random slices?);

Rationale: in this way, `data/gcs-public-data--healthcare-tcia-nsclc-radiomics/` can be left untouched and stored on separated hard drives which can be mounted when (and if) needed.