FROM ubuntu:18.04
#FROM nvidia/cuda:11.0-base
ARG DEBIAN_FRONTEND=noninteractive
#FROM nvcr.io/nvidia/tritonserver:21.05-py3
# Set a docker label to advertise multi-model support on the container
#LABEL com.amazonaws.sagemaker.capabilities.multi-models=true
# Set a docker label to enable container to use SAGEMAKER_BIND_TO_PORT environment variable if present
#LABEL com.amazonaws.sagemaker.capabilities.accept-bind-to-port=true

#RUN apt-get update
#RUN apt-get install -y python3
#RUN apt-get install -y python3-dev
#RUN apt-get install -y python3-pip
#RUN apt-get install -y libpython3.8-dev
#RUN apt-get install -y ffmpeg libsm6 libxext6
#RUN apt-get install -y git
#RUN apt-get install -y build-essential ca-certificates openjdk-8-jdk-headless curl
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-pip
RUN apt-get install -y libpython3.8-dev
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get install -y python3.8
RUN apt-get install -y ffmpeg libsm6 libxext6
RUN apt-get install -y git
RUN apt-get install -y build-essential ca-certificates openjdk-8-jdk-headless curl
RUN apt-get install -y libpq-dev

RUN python3 --version

RUN rm -f /usr/bin/python3 && ln -s /usr/bin/python3.8 /usr/bin/python3

RUN python3 --version

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

RUN python3 -m pip install numpy pandas botocore boto3 sagemaker-training sagemaker-inference fsspec s3fs model-archiver multi-model-server mxnet mxnet_cu101 sqlalchemy psycopg2 autogluon==0.4.0 pyarrow=='7.0.0'

# Copy entrypoint script to the image
COPY dockerd_entrypoint.py /usr/local/bin/dockerd-entrypoint.py
RUN chmod +x /usr/local/bin/dockerd-entrypoint.py
RUN mkdir -p /home/model-server/
ADD code /home/model-server

ENV DEFAULT_WORKERS_PER_MODEL 1
ENV MODEL_SERVER_TIMEOUT 600

# Define an entrypoint script for the docker image
ENTRYPOINT ["python3", "/usr/local/bin/dockerd-entrypoint.py"]
# Define command to be passed to the entrypoint
CMD ["serve"]