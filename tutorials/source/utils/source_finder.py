import glob
import os
import shutil
from pathlib import Path

from astropy.io import fits

import bdsf
from source.pre.exceptions import CatalogueException, SourceFinderException
from source.utils.bdsf_utils import gaul_as_df, srl_as_df


class SourceFinder:
    """
    Find sources using PyBDSF.


    Args:
        image_path (:obj:`str`): Path to the image in which to search for sources
    """

    def __init__(self, image_path):
        self.image_path = image_path
        self._run_complete = False

    @property
    def image_dirname(self):
        """
        Path of directory containing image
        """
        return os.path.dirname(self.image_path)

    @property
    def image_name(self):
        """
        Image file name
        """
        return os.path.basename(self.image_path)

    def get_srl_path(self):
        """
        Get BDSF source list path
        """
        return self.get_output_cat("srl")

    def get_gaul_path(self):
        """
        Get BDSF Gaussian list path
        """
        return self.get_output_cat("gaul")

    def get_bdsf_log_path(self):
        """
        Get BDSF log file path
        """
        return "{}.pybdsf.log".format(self.image_path)

    def get_bdsf_out_dir(self):
        """
        Get BDSF output directory
        """
        return "{}_pybdsm".format(self.image_path[:-5])

    def _get_bdsf_tmp_dir(self):
        """
        Get BDSF temp directory
        """
        return "{}_tmp".format(self.image_path[:-5])

    def get_output_cat(self, extn):
        """
        Get BDSF output directory
        """
        srl_glob = glob.glob(
            "{}_pybdsm/*/catalogues/*.{}".format(self.image_path[:-5], extn)
        )
        if len(srl_glob) == 1:
            return srl_glob[0]
        elif len(srl_glob) < 1:
            raise CatalogueException(
                "No output catalogue of type {} found".format(extn)
            )
        else:
            raise CatalogueException(
                "More than 1 catalogue of type {} found".format(extn)
            )

    def run( # one
        self,
        adaptive_rms_box=False,
        advanced_opts=True,
        atrous_do=False,
        psf_vary_do=False,
        psf_snrcut=5.0,
        psf_snrcutstack=10.0,
        output_opts=True,
        output_all=True,
        opdir_overwrite="overwrite",
        beam=(),
        blank_limit=None,
        thresh="hard",
        thresh_isl=4.0,
        thresh_pix=5.0,
        psf_snrtop=0.30,
        rms_map=True,
        rms_box=(),
        do_cache=True,
        **kwargs
    ):
        """
        Run the source finder algorithm.

        Args are the same as for the bdsf.process_image method, with sensible defaults
        submitted for any not given.

        The 'beam' and 'rms_box' arg defaults are determined from the image header if
        not provided.
        """
        self._run_complete = False

        # Must switch the executor's working directory to the image directory to
        # run PyBDSF, and switch back after the run is complete.
        cwd = os.getcwd()
        os.chdir(self.image_dirname)

        # Get beam info automatically if not provided
        if not beam:
            beam = self._get_beam_from_hdu()
        if not rms_box:
            rms_box = self._get_rms_box_from_hdu()

        # Run PyBDSF
        try:
            bdsf.process_image(
                self.image_name,
                adaptive_rms_box=adaptive_rms_box,
                advanced_opts=advanced_opts,
                atrous_do=atrous_do,
                psf_vary_do=psf_vary_do,
                psf_snrcut=psf_snrcut,
                psf_snrcutstack=psf_snrcutstack,
                output_opts=output_opts,
                output_all=output_all,
                opdir_overwrite=opdir_overwrite,
                beam=beam,
                blank_limit=blank_limit,
                thresh=thresh,
                thresh_isl=thresh_isl,
                thresh_pix=thresh_pix,
                psf_snrtop=psf_snrtop,
                rms_map=rms_map,
                rms_box=rms_box,
                do_cache=do_cache,
                **kwargs
            )
        except Exception as e:
            # Catch all exceptions to ensure CWD reverted
            os.chdir(cwd)
            raise e

        # Revert current working directory
        os.chdir(cwd)
        self.clean_tmp()
        self._run_complete = True

        return self.get_source_df()

    def _get_beam_from_hdu(self): #two
        """
        Look up the beam information in the header of the SourceFinder's image
        """
        try:
            with fits.open(self.image_name) as hdu:
                beam_maj = hdu[0].header["BMAJ"]
                beam_min = hdu[0].header["BMIN"]
                beam_pa = 0
                return (beam_maj, beam_min, beam_pa)
        except IndexError:
            raise SourceFinderException("Unable to automatically determine beam info")

    def _get_rms_box_from_hdu(self): #three
        """
        Determine an appropriate RMS box size using the header of the SourceFinder's
        image
        """
        try:
            with fits.open(self.image_name) as hdu:
                beam_maj = hdu[0].header["BMAJ"]
                pix_per_beam = beam_maj / hdu[0].header["CDELT2"]
                return (30 * pix_per_beam, 8 * pix_per_beam)
        except IndexError:
            raise SourceFinderException(
                "Unable to automatically determine RMS box size"
            )

    def get_source_df(self):
        """
        Given a gaussian list (.gaul) and source list (.srl) from PyBDSF, return a
        catalogue of sources, including the number of components.
        """
        gaul_df = gaul_as_df(self.get_gaul_path())
        srl_df = srl_as_df(self.get_srl_path())

        srl_df["n_gaussians"] = gaul_df["Source_id"].value_counts()

        return srl_df

    def reset(self):
        """
        Clean up previous BDSF run output
        """
        self._run_complete = False
        if os.path.isfile(self.get_bdsf_log_path()):
            os.remove(self.get_bdsf_log_path())
        if os.path.isdir(self.get_bdsf_out_dir()):
            shutil.rmtree(self.get_bdsf_out_dir())

    def clean_tmp(self):
        """
        Clean up BDSF temporary directory
        """
        if Path(self._get_bdsf_tmp_dir()).is_dir():
            shutil.rmtree(self._get_bdsf_tmp_dir())
