import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
from astropy.wcs import WCS
from astropy.wcs.utils import pixel_to_skycoord, skycoord_to_pixel

# Training area limits (RA, Dec)
TRAIN_LIM = {
    9200: {
        "ra_min": -0.04092,
        "ra_max": 0.0,
        "dec_min": -29.9400,
        "dec_max": -29.9074,
    },
    1400: {"ra_min": -0.2688, "ra_max": 0.0, "dec_min": -29.9400, "dec_max": -29.7265},
    560: {"ra_min": -0.6723, "ra_max": 0.0, "dec_min": -29.9400, "dec_max": -29.4061},
}


def update_header_from_cutout2D(hdu, cutout):
    """
    Update header for passed HDU from the Cutout2D object
    """
    newdata = np.zeros(
        (1, 1, cutout.data.shape[0], cutout.data.shape[1]), dtype=np.float32
    )
    newdata[0, 0, :, :] = cutout.data
    hdu.data = newdata

    # update header cards returned from cutout2D wcs:
    hdu.header.set("CRVAL1", cutout.wcs.wcs.crval[0])
    hdu.header.set("CRVAL2", cutout.wcs.wcs.crval[1])
    hdu.header.set("CRPIX1", cutout.wcs.wcs.crpix[0])
    hdu.header.set("CRPIX2", cutout.wcs.wcs.crpix[1])
    hdu.header.set("CDELT1", cutout.wcs.wcs.cdelt[0])
    hdu.header.set("CDELT2", cutout.wcs.wcs.cdelt[1])

    hdu.header.set("NAXIS1", cutout.wcs.pixel_shape[0])
    hdu.header.set("NAXIS2", cutout.wcs.pixel_shape[1])
    return hdu


def save_subimage(image_path, out_path, position, size, overwrite=True):
    """
    Write a sub-section of an image to a new FITS file.

    Adapted from https://docs.astropy.org/en/stable/nddata/utils.html

    Args:
        image_path (`str`): Path to input image
        out_path (`str`): Path to write sub-image to
        position (`tuple`): Pixel position of sub-image centre (x, y)
        size (`tuple`): Size in pixels of sub-image (ny, nx)
    """

    # Load the image and the WCS
    with fits.open(image_path) as image_hdu:
        wcs = WCS(image_hdu[0].header)
        cutout = Cutout2D(
            image_hdu[0].data[0, 0, :, :],
            position=position,
            size=size,
            wcs=wcs.celestial,
            mode="trim",
        )

        image_hdu[0] = update_header_from_cutout2D(image_hdu[0], cutout)
        image_hdu[0].writeto(out_path, overwrite=overwrite)
    return cutout


def crop_to_training_area(image_path, out_path, freq, pad_factor=1.0):
    """
    For a given SDC1 image, write a new FITS file containing only the training
    area.
    Training area defined by RA/Dec, which doesn't map perfectly to pixel values.

    Args:
        image_path (`str`): Path to input image
        out_path (`str`): Path to write sub-image to
        freq (`int`): [560, 1400, 9200] SDC1 image frequency (different training areas)
        pad_factor (`float`, optional): Area scaling factor to include edges
    """
    with fits.open(image_path) as image_hdu:
        wcs = WCS(image_hdu[0].header)

        # Lookup training limits for given frequency
        ra_max = TRAIN_LIM[freq]["ra_max"]
        ra_min = TRAIN_LIM[freq]["ra_min"]
        dec_max = TRAIN_LIM[freq]["dec_max"]
        dec_min = TRAIN_LIM[freq]["dec_min"]

        # Centre of training area pixel coordinate:
        tr_centre = SkyCoord(
            ra=(ra_max + ra_min) / 2,
            dec=(dec_max + dec_min) / 2,
            frame="fk5",
            unit="deg",
        )

        # Opposing corners of training area:
        tr_min = SkyCoord(ra=ra_min, dec=dec_min, frame="fk5", unit="deg",)
        tr_max = SkyCoord(ra=ra_max, dec=dec_max, frame="fk5", unit="deg",)

        # Training area approx width
        pixel_width = (
            abs(skycoord_to_pixel(tr_max, wcs)[0] - skycoord_to_pixel(tr_min, wcs)[0])
            * pad_factor
        )

        # Training area approx height
        pixel_height = (
            abs(skycoord_to_pixel(tr_max, wcs)[1] - skycoord_to_pixel(tr_min, wcs)[1])
            * pad_factor
        )

    save_subimage(
        image_path,
        out_path,
        skycoord_to_pixel(tr_centre, wcs),
        (pixel_height, pixel_width),
        overwrite=True,
    )


def get_image_centre_coord(image_path):
    """
    Given a fits image at image_path, return the SkyCoord corresponding to the
    image centre.
    """
    with fits.open(image_path) as image_hdu:
        x_size = image_hdu[0].header["NAXIS1"]
        y_size = image_hdu[0].header["NAXIS2"]

        return pixel_to_skycoord(x_size / 2, y_size / 2, WCS(image_hdu[0].header))


def get_pixel_value_at_skycoord(image_path, sky_coord):
    with fits.open(image_path) as image_hdu:
        x_pixel, y_pixel = skycoord_to_pixel(sky_coord, WCS(image_hdu[0].header))
        x_pixel = round(float(x_pixel))
        y_pixel = round(float(y_pixel))
        return image_hdu[0].data[0, 0, x_pixel, y_pixel]


def cat_df_from_srl_df(srl_df):
    """
    Load the source list output by PyBDSF and create a catalogue DataFrame of the
    form required for SDC1.

    Args:
        srl_path (`str`): Path to source list (.srl file)
    """
    # Instantiate catalogue DataFrame
    cat_df = pd.DataFrame()

    # Source ID
    cat_df["id"] = srl_df["Source_id"]

    # Positions (correct RA degeneracy to be zero)
    cat_df["ra_core"] = srl_df["RA_max"]
    cat_df.loc[cat_df["ra_core"] > 180.0, "ra_core"] -= 360.0
    cat_df["dec_core"] = srl_df["DEC_max"]

    cat_df["ra_cent"] = srl_df["RA"]
    cat_df.loc[cat_df["ra_cent"] > 180.0, "ra_cent"] -= 360.0
    cat_df["dec_cent"] = srl_df["DEC"]

    # Flux and core fraction
    cat_df["flux"] = srl_df["Total_flux"]
    cat_df["core_frac"] = (srl_df["Peak_flux"] - srl_df["Total_flux"]).abs()

    # Bmaj, Bmin (convert deg -> arcsec) and PA
    # Source list outputs FWHM as major/minor axis measures
    cat_df["b_maj"] = srl_df["Maj"] * 3600
    cat_df["b_min"] = srl_df["Min"] * 3600
    cat_df["pa"] = srl_df["PA"]

    # Size class
    cat_df["size"] = 2

    # Class
    # TODO: To be predicted using classifier
    cat_df["class"] = 1
    return cat_df
