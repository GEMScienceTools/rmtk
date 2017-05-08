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

RUN wget -q https://github.com/GEMScienceTools/rmtk/archive/$branch.tar.gz && \
    tar xzf $branch.tar.gz && mv rmtk-$branch rmtk && \
    ${HOME}/venv/bin/pip install -e rmtk

RUN virtualenv ${HOME}/venv
RUN ${HOME}/venv/bin/pip install -U pip wheel && \
    ${HOME}/venv/bin/pip install -r rmtk/requirements-py27-linux64.txt


EXPOSE 8888:8888
CMD cd rmtk && ${HOME}/venv/bin/ipython notebook --no-browser --ip=0.0.0.0
