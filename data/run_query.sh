#!/bin/bash

# help function
Help()
{
   echo
   echo "Run BigQuery query stored in 'input_file' and save the output in 'output_file'"
   echo
   echo "Syntax: run_query [-h] input_file output_file"
   echo "options:"
   echo "h     Print this Help."
   echo
}

while getopts ":h" option; do
   case $option in
      h) # display Help
         Help
         exit;;
   esac
done

QUERY_FILE=$1
OUTPUT_FILE=$2

bq query --max_rows=500 --headless --format=csv --project_id=idc-sandbox-000 --nouse_legacy_sql $(cat $QUERY_FILE) > $OUTPUT_FILE
