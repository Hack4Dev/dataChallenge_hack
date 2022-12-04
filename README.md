[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7038247.svg)](https://doi.org/10.5281/zenodo.7038247)


The aim of the tutorials is as  follows:
  - Source finding (RA, Dec) to locate the centroids and/or core positions,
  - Source property characterization (integrated flux density, possible core fraction, major and minor axis size, major axis position angle)
  - Source classification (one of SFG, AGN-steep, AGN-flat)


## Data
3 different simulated data are used in this workflow, where the simulation represents the following frequencies:
- 560 MHz
- 1400 MHz
- 9200 MHz


```bash
>  bash binder/download_sample_data.sh
```


## Hackathon Task
From the proposed pipeline, investigate new ways to find/classify sources.


## Prerequisites

All the libraries/dependencies necessary to run the tutorials are listed in the [requirements.txt](https://github.com/Hack4Dev/dataChallenge_hack/blob/master/requirements.txt) file.


## Installation

All the required libraries can be installed using pip and the [requirements.txt](https://github.com/Hack4Dev/dataChallenge_hack/blob/master/requirements.txt) file in the repo:

```bash
> pip install -r requirements.txt
```

### Would you like to clone this repository? Feel free!

```bash
> git clone https://github.com/Hack4Dev/dataChallenge_hack.git
```

Then make sure you have the right Python libraries for the tutorials. 


### New to Github?

The easiest way to get all of the lecture and tutorial material is to clone this repository. To do this you need git installed on your laptop. If you're working on Linux you can install git using apt-get (you might need to use sudo):

```
apt install git
```

You can then clone the repository by typing:

```
git clone https://github.com/Hack4Dev/dataChallenge_hack.git
```

To update your clone if changes are made, use:

```
cd dataChallenge_hack/
git pull
```

-----

