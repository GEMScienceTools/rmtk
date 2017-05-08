# vi:syntax=dockerfile
FROM ubuntu:xenial
MAINTAINER Daniele Viganò <daniele@openquake.org>

ARG branch=master

RUN apt-get update && apt-get install -y \
    wget python python-virtualenv python-pip

RUN useradd -u 1000 -d /home/openquake -m openquake

USER openquake
ENV HOME /home/openquake
WORKDIR ${HOME}

ADD https://api.github.com/repos/GEMScienceTools/rmtk/git/refs/heads/$branch /tmp/nocache.json

RUN wget -q https://github.com/GEMScienceTools/rmtk/archive/$branch.tar.gz && \
    tar xzf $branch.tar.gz && mv rmtk-$branch rmtk && rm $branch.tar.gz
RUN wget -q https://github.com/GEMScienceTools/rmtk_data/archive/master.tar.gz && \
    tar xzf master.tar.gz && mv rmtk_data-master rmtk_data && rm master.tar.gz

RUN virtualenv ${HOME}/venv
RUN ls -l rmtk
RUN ${HOME}/venv/bin/pip install -U pip wheel && \
    ${HOME}/venv/bin/pip install -r rmtk/requirements-py27-linux64.txt && \
    ${HOME}/venv/bin/pip install -e rmtk/

EXPOSE 8888:8888
CMD cd rmtk && ${HOME}/venv/bin/jupyter notebook --no-browser --ip=0.0.0.0 \
                                                 --NotebookApp.password='' \
                                                 --NotebookApp.token=''
