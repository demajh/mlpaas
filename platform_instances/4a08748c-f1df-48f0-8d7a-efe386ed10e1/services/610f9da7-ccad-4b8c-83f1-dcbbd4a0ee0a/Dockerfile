FROM ubuntu:18.04
ARG DEBIAN_FRONTEND=noninteractive

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

#RUN python3 -m pip install -r requirements.txt

RUN python3 -m pip install awslambdaric scipy numpy pandas botocore boto3 fsspec s3fs mxnet sqlalchemy psycopg2 autogluon pyarrow=='7.0.0'


WORKDIR ./
ADD handler.py ./

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]

CMD [ "handler.handler" ]