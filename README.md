[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/JColl88/sdc1-solution-binder/HEAD)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5526844.svg)](https://doi.org/10.5281/zenodo.5526844)

# Science Data Challenge 1 Tutorial Workflow

The SKA Science Data Challenge 1 (SDC1, https://astronomers.skatelescope.org/ska-science-data-challenge-1/) tasked participants with identifying and classifying sources in synthetic radio images.

Here we present a tutorial for producing a solution to this challenge that can easily be developed further.


## Development and execution environment


A small subsample of each image can be downloaded using the script `binder/download_sample_data.sh`, to excute the script run the following:

```bash
>  bash binder/download_sample_data.sh
```

Then make sure you have the right Python libraries for the tutorials. They can all be installed using pip and the requirements.txt file in the repo:

```bash
> pip install -r requirements.txt
```


After downloading the sample data you can start with the tutorials.
