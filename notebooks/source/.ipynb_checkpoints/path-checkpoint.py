import os
from pathlib import Path

def image_path(freq):
    return os.path.join("../data", "sample_images", "{}mhz_1000h.fits".format(freq))


def pb_path(freq):
    return os.path.join("../data", "sample_images", "{}mhz_pb.fits".format(freq))

def train_truth_path(freq):
    return os.path.join("../data", "truth", "{}mhz_truth_train.txt".format(freq))

def full_truth_path(freq):
    return os.path.join("../data", "truth", "{}mhz_truth_full.txt".format(freq))


# Output data paths
#
def train_source_df_path(freq):
    return os.path.join("../data", "sources", "{}mhz_sources_train.csv".format(freq))


def full_source_df_path(freq):
    return os.path.join("../data", "sources", "{}mhz_sources_full.csv".format(freq))


def submission_df_path(freq):
    return os.path.join("../data", "sources", "{}mhz_submission.csv".format(freq))


def model_path(freq):
    return os.path.join("../data", "models", "{}mhz_classifier.pickle".format(freq))


def score_report_path(freq):
    return os.path.join("../data", "score", "{}mhz_score.txt".format(freq))


def write_df_to_disk(df, out_path):
    """ Helper function to write DataFrame df to a file at out_path"""
    out_dir = os.path.dirname(out_path)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)