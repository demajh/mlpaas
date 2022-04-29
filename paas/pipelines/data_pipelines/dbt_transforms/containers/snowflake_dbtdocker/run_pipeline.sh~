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

# echo "Which virtual env"
# pip -V
# echo " Listing pip packages ..."
# pip freeze
# ls -l

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

# echo "-----------------"
# ls -l .
# echo "-----------------"
# ls -l dbtoncloud
# echo "-----------------"

echo "changing to dbt project folder : ${DBT_PROJECT}"
cd ${DBT_PROJECT}
# ls -l .

####################################################
##  Extract the secrets from the aws secrets manager and export the connection variables
####################################################
echo "Retrieving snowflake connecting info ..."

SFLK_INFO_PARSED=$(python3 ${HOME_DIR}/retrieve_secrets.py "${SFLK_INFO}" | grep "__SECRETS__" | sed 's/__SECRETS__//g')
#echo "SFLK INFO_PARSED : $SFLK_INFO_PARSED "

# We use python to extract json value instead of popular jq command, to keep docker size to minimal
# hence we are doing this extraction using python
export SNOWSQL_ACCOUNT=`python ${HOME_DIR}/extract_json_key.py  "$SFLK_INFO_PARSED" "SNOWSQL_ACCOUNT"`
export SNOWSQL_USER=`python ${HOME_DIR}/extract_json_key.py  "$SFLK_INFO_PARSED" "SNOWSQL_USER"`
export DBT_PASSWORD=`python ${HOME_DIR}/extract_json_key.py  "$SFLK_INFO_PARSED" "DBT_PASSWORD"`
export SNOWSQL_ROLE=`python ${HOME_DIR}/extract_json_key.py  "$SFLK_INFO_PARSED" "SNOWSQL_ROLE"`
export SNOWSQL_DATABASE=`python ${HOME_DIR}/extract_json_key.py  "$SFLK_INFO_PARSED" "SNOWSQL_DATABASE"`
export SNOWSQL_WAREHOUSE=`python ${HOME_DIR}/extract_json_key.py  "$SFLK_INFO_PARSED" "SNOWSQL_WAREHOUSE"`

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
