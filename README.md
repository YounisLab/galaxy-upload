# galaxy-upload

`galaxy-upload` is used to upload bigwig and bed files to [usegalaxy.org](https://usegalaxy.org/) and to generate links to view those files in [UCSC genome browser](https://genome.ucsc.edu/).

## Prerequisites

If using Docker, the only prerequisite is to install [docker CE](https://docs.docker.com/install/linux/docker-ce/ubuntu/).

If using outside of Docker, the requirements can be installed using

```
conda install -c bioconda --yes --file requirements.txt
sudo apt-get install lftp
```

## Building

```
docker image build -t galaxy-upload .
```

## Running

`galaxy-upload` can be run with and without Docker, though the latter is recommended.

Running `galaxy-upload` requires an account at [usegalaxy.org](https://usegalaxy.org/).

The API key for your galaxy account can be obtained from `User->Preferences->Manage API key`.

### Without Docker:

```
upload.py username api_key dir proj_name

  username    Username for usegalaxy.org.
  api_key     API key obtained from usegalaxy.org.
  dir         Directory of bigWig and junctions.bed files to upload.
  proj_name   Name to give track file. Existing track files with same name
              will be overwritten.

  Generated links can be found in {proj_name}_URL.txt in the same directory.
```

### With Docker:

TODO

