#!/bin/bash

#####################################################################################
# This script will get executed as part of the task execution. It does the following
#   - Creates a temp directory (/tmp/var/appdir)
#   - Copies the content from S3 bucket into /tmp/var/appdir
#   - Executes the script 'run_pipeline.sh'; found in the s3 bucket content
#####################################################################################

# set 

echo "========================================="
echo "Creating the workdir /tmp/var/appdir ..."
mkdir -p /tmp/var/appdir
cd /tmp/var/appdir

echo "Copying files from ${S3_CODE_BUCKET_DIR} ..."
aws s3 cp --recursive ${S3_CODE_BUCKET_DIR} .

# echo "========================================="
# ls -l .

chmod 777 ./run_pipeline.sh

./run_pipeline.sh

echo " ------------------------------------- "
echo " Finished!!! "
