FROM ubuntu:latest
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y g++
RUN apt-get install -y ffmpeg libsm6 libxext6
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

RUN python3 -m pip install \
    awslambdaric \
    pytz \
    numpy \
    pandas \
    python-dateutil \
    scipy \
    boto3 \
    jsonmerge \
    matplotlib \
    scikit-image \
    sagemaker

WORKDIR ./
ADD app.py ./

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]

CMD [ "app.handler" ]