# Bob Face Recognition
This repository serves as code base for my bachelor thesis on face recognition with low resolution images.

## Installation / Virtual Environment
1. First install [mambaforge](https://github.com/conda-forge/miniforge#mambaforge).
3. Create a virtual environment using `mamba` as follows:
```
mamba create --name bob_env --override-channels -c https://www.idiap.ch/software/bob/conda -c conda-forge python=3 bob.io.base bob.bio.face pytorch  
```
3. Activate the environement by `conda activate bob_env` and configure its channels as follows:
```
conda config --env --add channels conda-forge
conda config --env --add channels https://www.idiap.ch/software/bob/conda
```
4. Install packages by using `mamba install <package-name>`.

## Pipeline Setup
To successfully install the required packages for running the `simple_pipe.py` follow these steps:

1. Install buildout.cfg `pip install zc.buildout`.
2. Run buildout `buildout`. This should create a couple of folders and files.
3. Whenever `bob` or `python` is called through the terminal use `bin/bob` and `bin/python` instead.

## Feature Extraction
Install all necessary packages for `simple_pipe.py` and run the following command three times using `close`, `medium` and `far` each once as protocol.
```
bin/bob bio pipelines vanilla-biometrics scface-<protocol> ./simple_pipe.py -vvv -o samples_pipe_all -c --group eval
```
This runs the pipeline and saves all checkpoint data in a folder called `samples_pipe_all`. The extracted features used for this project can be found in the subdirectory called `samplewrapper-2`. To read the files simply use the terminal with the command `h5dump -y <filename>.h5`