[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/JColl88/sdc1-solution-binder/HEAD)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5526844.svg)](https://doi.org/10.5281/zenodo.5526844)

# Science Data Challenge 1 Solution Workflow

The SKA Science Data Challenge 1 (SDC1, https://astronomers.skatelescope.org/ska-science-data-challenge-1/) tasked participants with identifying and classifying sources in synthetic radio images.

Here we present an environment and workflow for producing a solution to this challenge that can easily be reproduced and developed further.

Instructions for setting up the (containerised) environment and running a simple workflow script using some Python helper modules are provided in this document.



## Development and execution environment


Download the data (from the project root folder `${SDC1_SOLUTION_ROOT}`):

```bash
$ /bin/bash scripts/download_data.sh
```


A small subsample of each image can be downloaded using the script `binder/download_sample_data.sh`.

After downloading the sample data an example workflow notebook is provided at `analyse_sample.ipynb`.
