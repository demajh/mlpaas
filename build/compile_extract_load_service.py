import os
import sys
import json
import distutils.dir_util
from code_generator import CodeGenerator

SERVICE_ID = sys.argv[1]
INSTANCE_SERVICES_PATH = sys.argv[2]
INSTANCE_SERVICES_PATH = os.path.join(INSTANCE_SERVICES_PATH, SERVICE_ID)
SERVICE_TEMPLATE_PATH = sys.argv[3]
CONFIGNAME = os.environ['INSTANCE_CONFIG']
SERVICE_TEMPLATE_DRIVER_PATH = os.path.join(SERVICE_TEMPLATE_PATH, "handler.py")
SERVICE_DOCKERFILE_PATH = os.path.join(SERVICE_TEMPLATE_PATH, "Dockerfile")

config = json.load(open(CONFIGNAME, "r"))
extract_source = config["extract_source"]
extract_source_name = config["extract_source_name"]
load_target = config["load_target"]
load_target_name = config["load_target_name"]
database = config["database_name"]
database_region = config["database_region"]
user = config["database_user"]
password = config["database_password"]
host = config["database_host"]
port = config["database_port"]
schema = config["database_schema"]
iam_role = config["iam_role_arn"]

code_generator = CodeGenerator()
extract_source_code_str = code_generator.generate_extract_data(extract_source, extract_source_name)
load_target_code_str = code_generator.generate_load_target(load_target, load_target_name)
#sync_source_target_code_str = code_generator.generate_sync_source_target(extract_source)

INSTANCE_SERVICE_DRIVER_PATH = os.path.join(INSTANCE_SERVICES_PATH, "handler.py")
INSTANCE_SERVICE_DOCKERFILE_PATH = os.path.join(INSTANCE_SERVICES_PATH, "Dockerfile")
distutils.dir_util.copy_tree(SERVICE_TEMPLATE_PATH, INSTANCE_SERVICES_PATH)

service_template = open(INSTANCE_SERVICE_DRIVER_PATH, "r").read()
service_template = service_template.replace("{extract_source}", "'{}'".format(extract_source))
service_template = service_template.replace("{extract_source_name}", "'{}'".format(extract_source_name))
service_template = service_template.replace("{load_target}", "'{}'".format(load_target))
service_template = service_template.replace("{load_target_name}", "'{}'".format(load_target_name))
service_template = service_template.replace("{extract_source_code_location}", extract_source_code_str)
service_template = service_template.replace("{database_name}", "'{}'".format(database))
service_template = service_template.replace("{database_region}", "'{}'".format(database_region))
service_template = service_template.replace("{database_user}", "'{}'".format(user))
service_template = service_template.replace("{database_password}", "'{}'".format(password))
service_template = service_template.replace("{database_host}", "'{}'".format(host))
service_template = service_template.replace("{database_port}", "'{}'".format(port))
service_template = service_template.replace("{database_schema}", "'{}'".format(schema))
service_template = service_template.replace("{iam_role}", "'{}'".format(iam_role))
service_template = service_template.replace("{create_load_target_code_location}", load_target_code_str)
service_template = service_template.replace("{sync_source_target_code_location}", "")

print(service_template)
print(INSTANCE_SERVICE_DRIVER_PATH)
print("\{extract_source\}" in service_template)
print("{database_port}" in service_template)
print(type(service_template))

with open(INSTANCE_SERVICE_DRIVER_PATH, "w") as fhand:
    fhand.write(service_template)

