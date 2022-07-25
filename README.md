# Bob Face Recognition
This repository serves as code base for my bachelor thesis on face recognition with low resolution images.

## Installation / Virtual Environment (Linux)
1. First install [mambaforge](https://github.com/conda-forge/miniforge#mambaforge).
2. Configure your conda installation by executing the following commands:
```
conda install -n base -c conda-forge mamba
mamba update -n base -c conda-forge conda mamba
conda config --set show_channel_urls True
```
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
bin/bob bio pipelines vanilla-biometrics scface-<protocol> ./helpers/simple_pipe.py -vvv -o samples_pipe_all -c --group eval
```
This runs the pipeline and saves all checkpoint data in a folder called `samples_pipe_all`. The extracted features used for this project can be found in the subdirectory called `samplewrapper-2`. To read the files simply use the terminal with the command `h5dump -y <filename>.h5`

## Running the Code
Use the terminal for starting the script with the command `bin/python main.py`. The following options are available:
* --protocol, -p\
Choose between `close`, `medium` or `far` protocol used for the comparison (default: `all`)
* --comparison_method, -c\
Specify a comparison method (default: `all`)

| Approach                                                                         | Comparison Methods                                                                                    |
|----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| direct comparison                                                                | `baseline`                                                                                            |
| rank list comparison (use `rank_list_comparison` to run all methods)             | `mueller2010`, `mueller2013`, `schroff`, `wartmann`, `kendall`, `weighted_kendall`, `spearman`        |
| standardization comparison (use `standardization_comparison` to run all methods) | `braycurtis`, `canberra`, `chebyshev`, `cityblock`, `cosine`, `euclidean`, `minkowski`, `sqeuclidean` |

* --standardization_method, -s\
Select `standardize`, `subtract_mean` or `omitted` to define the preprocessing of the lists with cosine distances. This argument is only important whenever methods for a standardization comparison are chosen (default: `standardize`).
* --record_output, -r\
Include to record scores such as recognition rates, runtime and score files (default: `False`)
* --enable_larger_cohort, -lc\
Include to extend the cohort with 43 samples (default: `False`)

## Evaluation of Results
If the recording of scores is enabled, an output folder is created in which there are `.csv` files for every comparison method and protocol used for verification as well as a `.txt` file containing the recognition rates and averaged runtimes used for identification.\
To evaluate the verification results use the following command including the files you wish to visualize:
```
bin/bob bio roc -v -o <output-filename>.pdf -ts "<graph-title>" -lg <line-names> <csv-files>
```

## Observations
The following properties were observed:
* The rank list comparison method `spearman` has the same results (both identification and verification) as the method `schroff`, however the latter proves to be faster in execution.
* The standardization comparison method `sqeuclidean` trivially has the same results (both identification and verification) as the method `euclidean`, however proves to be faster in execution.
* If `p=2` is chosen for the standardization comparison method `minkowski` the results (both identification and verification) are the same as `euclidean` and `sqeuclidean` by means of definition, however the method is faster than `euclidean`.
* The standardization comparison method `cosine` has the same results (both identification and verification) as the method `sqeuclidean` for `standardize` preprocessing, however proves to be slower in execution.
* The standardization comparison methods `cosine` and `braycurtis` have the same verification results for `standardize` and `subtract_mean` and are used with the latter for comparison to rank list comparison methods.
