#!/bin/sh

mkdir -p data/sample_images
mkdir -p data/truth

Samples of the 1000 hour simulated images
wget -O data/sample_images/560mhz_1000h.fits https://www.dropbox.com/s/z1wdeqpq7ae0rqq/560mhz_1000h_sample.fits
wget -O data/sample_images/1400mhz_1000h.fits https://www.dropbox.com/s/o3hvchtrv08z3u3/1400mhz_1000h_sample.fits
wget -O data/sample_images/9200mhz_1000h.fits https://www.dropbox.com/s/vcprub2b4hzq54x/9200mhz_1000h_sample.fits

# Primary beam images
wget -O data/sample_images/560mhz_pb.fits https://owncloud.ia2.inaf.it/index.php/s/ZbaSDe7zGBYgxL1/download
wget -O data/sample_images/1400mhz_pb.fits https://owncloud.ia2.inaf.it/index.php/s/tVGse9GaLBQmntc/download
wget -O data/sample_images/9200mhz_pb.fits https://owncloud.ia2.inaf.it/index.php/s/HlEJNsN2Vd4RL9W/download

# Training truth catalogues (for model training)
wget -O data/truth/560mhz_truth_train.txt https://owncloud.ia2.inaf.it/index.php/s/iTOVkIL6EfXkcdR/download
wget -O data/truth/1400mhz_truth_train.txt https://owncloud.ia2.inaf.it/index.php/s/0HMJmNhPywxQdY4/download
wget -O data/truth/9200mhz_truth_train.txt https://owncloud.ia2.inaf.it/index.php/s/Y5CIa5V3QiBu1M1/download

# Full truth catalogues (for scoring)
wget -O data/truth/560mhz_truth_full.txt https://owncloud.ia2.inaf.it/index.php/s/CZENkk6JdyVqIHw/download
wget -O data/truth/1400mhz_truth_full.txt https://owncloud.ia2.inaf.it/index.php/s/J2WFVTsFevJBHKj/download
wget -O data/truth/9200mhz_truth_full.txt https://owncloud.ia2.inaf.it/index.php/s/Vao072pgtP9NESB/download