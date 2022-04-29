import os
import sys
import json
from code_generator import CodeGenerator

PLATFORM_INSTANCE_PIPELINES_PATH = sys.argv[1]
PLATFORM_INSTANCE_INFRASTRUCTURE_PATH = sys.argv[2]
PIPELINES_PAYLOAD = sys.argv[3]
PLATFORM_INSTANCE_INFRASTRUCTURE_SOURCE_PATH = os.path.join(PLATFORM_INSTANCE_INFRASTRUCTURE_PATH,
                                                            "infrastructure/infrastructure_stack.py")
PIPELINES_PAYLOAD = json.loads(PIPELINES_PAYLOAD)
code_generator = CodeGenerator()

ml_pipelines_infrastructure = ""
for pipeline_type, pipeline_descriptors in list(PIPELINES_PAYLOAD.items()):
    cloud_provider, \
    pipeline_resource_type, \
    pipeline_id = pipeline_descriptors
    pipeline_image_path = os.path.join(PLATFORM_INSTANCE_PIPELINES_PATH, service_id)

    pipeline_infrastructure_code_str = code_generator.generate_pipeline_infrastructure(cloud_provider,
                                                                                       pipeline_type,
                                                                                       pipeline_resource_type,
                                                                                       pipeline_image_path)

    ml_pipelines_infrastructure += pipeline_infrastructure_code_str + "\n\n"

infrastructure_template = open(PLATFORM_INSTANCE_INFRASTRUCTURE_SOURCE_PATH, "r").read()
infrastructure_template = infrastructure_template.replace("{ml_pipeline_infrastructure}",
                                                          "{}".format(ml_pipelines_infrastructure))

with open(PLATFORM_INSTANCE_INFRASTRUCTURE_SOURCE_PATH, "w") as fhand:
    fhand.write(infrastructure_template)



