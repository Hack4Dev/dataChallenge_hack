import os

import numpy as np
from astropy import units as u
from astropy.io import fits
from MontagePy.main import mGetHdr, mProjectQL
from source.pre.exceptions import ImageNotPreprocessed
from source.utils.image_utils import (
    crop_to_training_area,
    get_image_centre_coord,
    get_pixel_value_at_skycoord,
    save_subimage,
)


class Sdc1Image:
    """
    Class to handle image preprocessing for SDC1.

    The Sdc1Image instance contains simple metadata about the SDC1 image, such as
    frequency and the paths to the files on disk, and provides methods to perform
    preprocessing of the images.

    Args:
        freq (:obj:`int`): Image frequency band (560, 1400 or 9200 MHz)
        path (:obj:`str`): Path to SDC1 raw image
        pb_path (:obj:`str`): Path to corresponding PrimaryBeam image
    """

    def __init__(self, freq, path, pb_path):
        self._freq = freq
        self._path = path
        self._pb_path = pb_path
        self._prep = False

        self._train = None
        self._pb_corr_image = None

    @property
    def freq(self):
        """
        Image frequency band (560, 1400 or 9200 MHz)
        """
        return self._freq

    @property
    def path(self):
        """
        Path to SDC1 raw image
        """
        return self._path

    @property
    def dirname(self):
        """
        Path of directory containing image
        """
        return os.path.dirname(self._path)

    @property
    def pb_path(self):
        """
        Path to corresponding PrimaryBeam image
        """
        return self._pb_path

    @property
    def prep(self):
        """
        Boolean which states whether image preprocessing has been performed
        """
        return self._prep

    @property
    def train(self):
        """
        Path to training image (if self.prep=True)
        """
        if self.prep:
            return self._train
        else:
            raise ImageNotPreprocessed("No training image, image not preprocessed")

    @property
    def pb_corr_image(self):
        """
        Path to primary beam corrected image (if self.prep=True)
        """
        if self.prep:
            return self._pb_corr_image
        else:
            raise ImageNotPreprocessed("No PB-corrected image, image not preprocessed")

    # def preprocess(self):
    #     """
    #     Perform preprocessing steps:
    #         1) Create PB-corrected image (self.pb_corr_image)
    #         2) Output separate training image (self.train)
    #     """
    #     self._prep = False
    #     self._create_pb_corr()
    #     self._create_train()
    #     self._prep = True

    def reset(self):
        """
        Reset the state of the Sdc1Image instance by deleting train and PB-corrected
        images
        """
        self._delete_pb_corr()
        self._delete_train()

    def _get_pb_cut_path(self):
        """
        PB cutout path (temporary)
        """
        return self._pb_path[:-5] + "_cut.fits"

    def _get_pb_cut_rg_path(self):
        """
        PB cutout regridded path (temporary)
        """
        return self._pb_path[:-5] + "_cut_rg.fits"

    def _get_hdr_path(self):
        """
        Montage header file, used for reproject (temporary)
        """
        return os.path.join(self.dirname, "hdu_tmp.hdr")

    def _create_train(self, pad_factor=1.0):
        """
        Create the training image (crop to the frequency-dependent training area)
        """
        self._train = None
        train_path = self.path[:-5] + "_train.fits"
        crop_to_training_area(self._pb_corr_image, train_path, self.freq, pad_factor)
        self._train = train_path

    def _delete_train(self):
        """
        Delete the training image
        """
        if self._train is None:
            return
        if os.path.exists(self._train):
            os.remove(self._train)
        self._train = None

    def _create_pb_corr(self, threshold=0.1):
        """
        Apply PB correction to the image at self.path, using the primary beam
        file at self.pb_path.

        This uses Montage to regrid the primary beam image to the same pixel scale
        as the image to be corrected.
        """
        self._pb_corr_image = None

        # Establish input image to PB image pixel size ratios:
        with fits.open(self.pb_path) as pb_hdu:
            pb_x_pixel_deg = pb_hdu[0].header["CDELT2"]
        with fits.open(self.path) as image_hdu:
            x_size = image_hdu[0].header["NAXIS1"]
            x_pixel_deg = image_hdu[0].header["CDELT2"]

        ratio_image_pb_pix = (x_size * x_pixel_deg) / pb_x_pixel_deg
        coord_image_centre = get_image_centre_coord(self.path)

        if ratio_image_pb_pix < 2.0:
            # Image not large enough to regrid (< 2 pixels in PB image);
            # apply simple correction
            pb_value = get_pixel_value_at_skycoord(self.pb_path, coord_image_centre)
            self._apply_pb_corr(pb_value)
            return

        with fits.open(self.pb_path) as pb_hdu:
            # Create cropped PB image larger than the input image
            # TODO: May be inefficient when images get large
            size = (
                x_size * x_pixel_deg * u.degree * 2,
                x_size * x_pixel_deg * u.degree * 2,
            )

            save_subimage(
                self.pb_path,
                self._get_pb_cut_path(),
                coord_image_centre,
                size,
                overwrite=True,
            )

        # Regrid image PB cutout to same pixel scale as input image
        mGetHdr(self.path, self._get_hdr_path())

        # TODO: mProjectQL better than mProject, which outputs too-small images?
        rtn = mProjectQL(
            input_file=self._get_pb_cut_path(),
            output_file=self._get_pb_cut_rg_path(),
            template_file=self._get_hdr_path(),
        )
        if rtn["status"] == "1":
            raise ImageNotPreprocessed(
                "Unable to reproject image: {}".format(rtn["msg"])
            )
     
        # Correct Montage output (convert to 32-bit and fill NaNs)
        pb_array = self._postprocess_montage_out()

        if threshold > 0:
            pb_array[pb_array < threshold] = np.nan
        
        # Apply PB correction and delete temporary files
        self._apply_pb_corr(pb_array)
        self._cleanup_pb()

    def _delete_pb_corr(self):
        """
        Delete the PB-corrected image
        """
        if self._pb_corr_image is None:
            return
        if os.path.exists(self._pb_corr_image):
            os.remove(self._pb_corr_image)
        self._pb_corr_image = None

    def _postprocess_montage_out(self):
        """
        Montage outputs the regridded PB image using 64-bit floats, and pads edges
        with NaN values - fix these issues.
        """
        with fits.open(self._get_pb_cut_rg_path(), mode="update") as pb_hdu:
            newdata = np.zeros(
                (1, 1, pb_hdu[0].data.shape[0], pb_hdu[0].data.shape[1]),
                dtype=np.float32,
            )
            newdata[0, 0, :, :] = pb_hdu[0].data
            # NAXIS will automatically update to 4 in the header
            pb_hdu[0].data = newdata

            # Fix NaNs introduced in PB by Montage at edges
            # TODO: This may not be performing correctly, check
            mask = np.isnan(pb_hdu[0].data)
            pb_hdu[0].data[mask] = np.interp(
                np.flatnonzero(mask), np.flatnonzero(~mask), pb_hdu[0].data[~mask]
            )
            pb_array = pb_hdu[0].data
            pb_hdu.flush()
        return pb_array

    def _apply_pb_corr(self, pb_data):
        """
        Apply the PB correction and write to disk.

        pb_data can either be an array of the same dimensions as the image at
        self.path, or a scalar.
        """
        pb_corr_path = self.path[:-5] + "_pbcor.fits"
        with fits.open(self.path) as image_hdu:
            image_hdu[0].data = image_hdu[0].data / pb_data
            image_hdu[0].writeto(pb_corr_path, overwrite=True)
        self._pb_corr_image = pb_corr_path

    def _cleanup_pb(self):
        """
        Remove temporary files created to apply PB correction
        """
        for tempfile in [
            self._get_pb_cut_path(),
            self._get_pb_cut_rg_path(),
            self._get_hdr_path(),
        ]:
            if os.path.exists(tempfile):
                os.remove(tempfile)
