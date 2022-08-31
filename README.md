[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7038247.svg)](https://doi.org/10.5281/zenodo.7038247)

# Science Data Challenge 1 Tutorial Workflow
This tutorial is based on the SKA Data Challenge 1. The aim of the tutorial is to learn to identify and classify sources in radio images. The data provided is simulated, to represent what the SKA data will look like once the telescope is in operation.


The aim of the tutorial is as  follows:
  - Source finding (RA, Dec) to locate the centroids and/or core positions,
  - Source property characterization (integrated flux density, possible core fraction, major and minor axis size, major axis position angle)
  - Source classification (one of SFG, AGN-steep, AGN-flat)



## Development and execution environment


```bash
> git clone https://github.com/Hack4Dev/apple_classification.git
```

A small subsample of each image can be downloaded using the script `binder/download_sample_data.sh`, to excute the script run the following:

```bash
>  bash binder/download_sample_data.sh
```

Then make sure you have the right Python libraries for the tutorials. They can all be installed using pip and the requirements.txt file in the repo:

```bash
> pip install -r requirements.txt
```


-----

### New to Github?

The easiest way to get all of the lecture and tutorial material is to clone this repository. To do this you need git installed on your laptop. If you're working on Linux you can install git using apt-get (you might need to use sudo):

```
apt install git
```

You can then clone the repository by typing:

```
git clone https://github.com/Hack4Dev/apple_classification.git
```

To update your clone if changes are made, use:

```
cd apple_classification/
git pull
```

-----
