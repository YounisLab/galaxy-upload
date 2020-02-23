FROM continuumio/miniconda:4.5.11

WORKDIR /home

RUN conda config --add channels conda-forge
RUN conda config --add channels bioconda

COPY requirements.txt /home

RUN conda install --yes --file requirements.txt

# install lftp from package manager
RUN apt-get update && apt-get install -y lftp

CMD ["/bin/bash"]
