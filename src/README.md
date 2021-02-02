# `src` subdir

All the source code goes here.

## To-Dos

### Documentation & Commenting
- [ ] Double check the in-code documentation (functions help, comments, etc.);

### Pre-processing Pipeline

#### Conversion of the notebooks into python scripts:
- [x] Check out `plastimatch` (use it to convert RTSTRUCT to .NRRD);
- [x] Find the best library to load .NRRD (itk-python/SimpleITK)
- [x] Script the pre-processing pipeline;
- [x] Double check all the code to make sure orientations etc. are ok;
- [ ] Eventually get rid of all the`z_first` params?
- [x] Export the full dataset in an input-friendly format (don't forget to save a couple of .png along with the other files!);

#### Data polishing/
- [x] Take care of exceptions prior to the cropping phase;
- [x] Add log of the center of mass (to handle `bbox` exceptions);
- [x] Take care of exceptions in the masks (e.g., more/less than two classes);
- [x] Populate a CSV file with information about each volume in the dataset (original size, size 1mm, exceptions... etc.);


### Study Replication

#### Deep Learning model:

- [ ] Select a subset of data for which no exceptions are found;
- [ ] Volumes normalisation as done in ModelHub;
- [ ] Evaluate the results and compute ROC AUCs;

#### Radiomics model:

- [ ] Features quantisation + MRMR features selection;