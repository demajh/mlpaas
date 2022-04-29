#!/bin/bash

HOME_DIR=${PWD}
DBT_PACKAGED_FOLDER=dbtvenvs  #Folder in which DBT packaged as virtual env is stored
DBT_DATAOPS_FOLDER=dbtdataops #Folder in which various DBT data transformation projects are packaged and stored

####################################################
##  The following steps are for extracting the dbt packaged dbt project and sourcing the virtual env
####################################################

tar -zxf ${DBT_PACKAGED_FOLDER}/dbt_python_venv.tar.gz .

echo " Activating virtual env ... "
source bin/activate

####################################################
##  The following steps are for extracting the specific dbt project identified by 'DBT_PROJECT'
####################################################
# echo "Switching to DBT_DATAOPS_FOLDER : ${DBT_DATAOPS_FOLDER} "
cd ./${DBT_DATAOPS_FOLDER}
# echo "DBT project : >${DBT_PROJECT}<"
# echo "PWD : ${PWD}"
ls -l 

# untar the dbt project based of env variable : DBT_PROJECT_PACKAGED_FLNAME_WITH_PATH
tar -zxf ${DBT_PROJECT}*

echo "changing to dbt project folder : ${DBT_PROJECT}"
cd ${DBT_PROJECT}
# ls -l .

####################################################
##  Extract the secrets from the aws secrets manager and export the connection variables
####################################################
echo "Retrieving snowflake connecting info ..."

####################################################
##  Invoke the DBT model
####################################################
export DBT_PROFILES_DIR=./

# dbt --help

echo " ------------------------------------- "
echo "Executing dbt script : ${DBT_RUN_SCRIPT} ..."
chmod 750 ${DBT_RUN_SCRIPT}

./${DBT_RUN_SCRIPT}

echo " ------------------------------------- "
echo " Finished!!! "
