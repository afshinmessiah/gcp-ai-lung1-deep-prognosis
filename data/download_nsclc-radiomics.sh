#!/bin/bash

INPUT_TABLE=$1
DOWNLOAD_DIR="nsclc-radiomics/dicom"
CT_STUDY_INSTANCE_UID_LIST="ct_study_instance_uid_download.txt"
GS_URI_LIST="gsutil_manifesto.txt"

if [ -f $CT_STUDY_INSTANCE_UID_LIST ] ; then
    rm $CT_STUDY_INSTANCE_UID_LIST
fi

cat $INPUT_TABLE | tail -n +2 | cut -d "," -f2 >> $CT_STUDY_INSTANCE_UID_LIST

mkdir -p nsclc-radiomics
mkdir -p $DOWNLOAD_DIR

#cat gsutil_manifesto.txt | gsutil -u idc-sandbox-000 -m cp -Ir $DOWNLOAD_DIR

for ct_uid in  $(cat $CT_STUDY_INSTANCE_UID_LIST); do
	echo "gs://idc-tcia-nsclc-radiomics/dicom/${ct_uid}" >> $GS_URI_LIST
done

rm $CT_STUDY_INSTANCE_UID_LIST

cat $GS_URI_LIST | gsutil -u idc-sandbox-000 -m cp -Ir $DOWNLOAD_DIR
