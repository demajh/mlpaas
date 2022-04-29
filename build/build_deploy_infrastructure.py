import os
import sys
import subprocess

CLOUD_PROVIDER = sys.argv[1]
IAC_FRAMEWORK = sys.argv[2]
PLATFORM_INSTANCE_INFRASTRUCTURE_PATH = sys.argv[3]

if CLOUD_PROVIDER == "aws" and IAC_FRAMEWORK == "cdk":

    wd = os.getcwd()
    os.chdir(PLATFORM_INSTANCE_INFRASTRUCTURE_PATH)
    subprocess.check_call(["cdk", "bootstrap"])
    subprocess.check_call(["cdk", "deploy"])
    os.chdir(wd)

else:

    raise Exception("Unrecognized cloud_provider/iac_framework combination!!  Given values are {} and {}.".format(CLOUD_PROVIDER,
                                                                                                                  IAC_FRAMEWORK))



