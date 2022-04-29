import os
import sys
import json
from code_generator import CodeGenerator

PLATFORM_INSTANCE_SERVICES_PATH = sys.argv[1]
PLATFORM_INSTANCE_INFRASTRUCTURE_PATH = sys.argv[2]
SERVICES_PAYLOAD = sys.argv[3]
PLATFORM_INSTANCE_INFRASTRUCTURE_SOURCE_PATH = os.path.join(PLATFORM_INSTANCE_INFRASTRUCTURE_PATH,
                                                            "infrastructure/infrastructure_stack.py")
SERVICES_PAYLOAD = json.loads(SERVICES_PAYLOAD)
code_generator = CodeGenerator()

ml_services_infrastructure = ""
for service_type, service_descriptors in list(SERVICES_PAYLOAD.items()):
    cloud_provider, \
    service_resource_type, \
    service_id, \
    service_role_identifiers = service_descriptors
    service_image_path = os.path.join(PLATFORM_INSTANCE_SERVICES_PATH, service_id)

    service_infrastructure_code_str = code_generator.generate_service_infrastructure(cloud_provider,
                                                                                     service_type,
                                                                                     service_resource_type,
                                                                                     service_role_identifiers,
                                                                                     service_image_path)

    ml_services_infrastructure += service_infrastructure_code_str + "\n\n"


infrastructure_template = open(PLATFORM_INSTANCE_INFRASTRUCTURE_SOURCE_PATH, "r").read()
infrastructure_template = infrastructure_template.replace("{ml_services_infrastructure}",
                                                          "{}".format(ml_services_infrastructure))

with open(PLATFORM_INSTANCE_INFRASTRUCTURE_SOURCE_PATH, "w") as fhand:
    fhand.write(infrastructure_template)



