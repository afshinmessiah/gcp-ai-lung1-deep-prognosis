#!/bin/bash

# help function
Help()
{
   echo
   echo "Update packages information and install packages specified in 'input_file'"
   echo
   echo "Syntax: setup_vm [-h] input_file"
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

REQUIREMENTS_FILE=$1

sudo apt update

for package in $(cat $REQUIREMENTS_FILE); do
	sudo apt install $package
done
