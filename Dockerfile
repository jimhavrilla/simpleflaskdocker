FROM centos/python-38-centos7
USER root
RUN yum install musl-dev linux-headers g++ gcc git curl
RUN yum clean all
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m pip install wheel
RUN pip install -r requirements.txt
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
COPY . /code
RUN chmod +x /code/app_init.sh
ENTRYPOINT sh /code/app_init.sh
