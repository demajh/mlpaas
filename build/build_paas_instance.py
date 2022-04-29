import os
import sys
import json
import uuid
import subprocess
import distutils.dir_util

# Initialize platform instance
CONFIGNAME=sys.argv[1]
os.environ['INSTANCE_CONFIG'] = CONFIGNAME
config = json.load(open(CONFIGNAME, "r"))

root_directory = config["root_directory"]
cloud_provider = config["cloud_provider"]
iac_framework = config["iac_framework"]
iam_role_name = config["iam_role_name"]
iam_role_arn = config["iam_role_arn"]
role_identifiers = [iam_role_name, iam_role_arn]

services = config["services"]
service_types = list(services.keys())
service_template_paths = {"extract_load": os.path.join(root_directory, "mlpaas/paas/services/serverless/extract_load")}
infrastructure_template_path = os.path.join(root_directory, "mlpaas/paas/infrastructure/{}/{}".format(cloud_provider, iac_framework))
platform_instance_id = str(uuid.uuid4())
platform_instance_path = os.path.join(root_directory, "mlpaas/platform_instances/{}".format(platform_instance_id))
platform_instance_services_path = os.path.join(root_directory, "mlpaas/platform_instances/{}/services".format(platform_instance_id))
platform_instance_pipelines_path = os.path.join(root_directory, "mlpaas/platform_instances/{}/pipelines".format(platform_instance_id))
platform_instance_experiments_path = os.path.join(root_directory, "mlpaas/platform_instances/{}/experiments".format(platform_instance_id))
platform_instance_visualization_path = os.path.join(root_directory, "mlpaas/platform_instances/{}/visualization".format(platform_instance_id))
platform_instance_infrastructure_path = os.path.join(root_directory, "mlpaas/platform_instances/{}/infrastructure".format(platform_instance_id))

if not os.path.exists(platform_instance_path):
    os.makedirs(platform_instance_path)
    os.makedirs(platform_instance_services_path)
    os.makedirs(platform_instance_pipelines_path)
    os.makedirs(platform_instance_experiments_path)
    os.makedirs(platform_instance_visualization_path)
    os.makedirs(platform_instance_infrastructure_path)

# Initialize platform instance infrastructure
distutils.dir_util.copy_tree(infrastructure_template_path,
                             platform_instance_infrastructure_path)

# Build data services
compiled_data_services = {}
supported_data_service_types = ["extract_load", "dbt_transform", "spark_transform"]
if "extract_load" in service_types:
    service_id = str(uuid.uuid4())
    service_resource_type = config["services"]["extract_load"]
    service_template_path = service_template_paths["extract_load"]
    subprocess.check_call(["python3", "compile_extract_load_service.py", service_id, platform_instance_services_path, service_template_path])
    compiled_data_services["extract_load"] = [cloud_provider,
                                              service_resource_type,
                                              service_id,
                                              role_identifiers]
data_service_build_payload = json.dumps(compiled_data_services)
subprocess.check_call(["python3",
                       "build_data_services.py",
                       platform_instance_services_path,
                       platform_instance_infrastructure_path,
                       data_service_build_payload])

# Build data pipeline
compiled_data_pipelines = {}
data_pipeline_build_payload = json.dumps(compiled_data_pipelines)
subprocess.check_call(["python3",
                       "build_data_pipelines.py",
                       platform_instance_pipelines_path,
                       platform_instance_infrastructure_path,
                       data_pipeline_build_payload])

# Build ML services
compiled_ml_services = {}
ml_service_build_payload = json.dumps(compiled_ml_services)
subprocess.check_call(["python3",
                       "build_ml_services.py",
                       platform_instance_pipelines_path,
                       platform_instance_infrastructure_path,
                       ml_service_build_payload])

# Build ML pipelines
compiled_ml_pipelines = {}
ml_pipeline_build_payload = json.dumps(compiled_ml_pipelines)
subprocess.check_call(["python3",
                       "build_ml_pipelines.py",
                       platform_instance_pipelines_path,
                       platform_instance_infrastructure_path,
                       ml_pipeline_build_payload])

# Build and deploy infrastructure
subprocess.check_call(["python3",
                       "build_deploy_infrastructure.py",
                       cloud_provider,
                       iac_framework,
                       platform_instance_infrastructure_path])



