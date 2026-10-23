import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from dotenv import load_dotenv

from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    DataCollection,
    MimeType,
    BBox,
    CRS,
)


# ==========================================
# 1. Load Copernicus credentials
# ==========================================

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

config = SHConfig()

config.sh_client_id = client_id
config.sh_client_secret = client_secret

config.sh_token_url = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

config.sh_base_url = "https://sh.dataspace.copernicus.eu"


# ==========================================
# 2. Sentinel-2 collection
# ==========================================

sentinel2 = DataCollection.SENTINEL2_L2A.define_from(
    "s2l2a",
    service_url=config.sh_base_url
)


# ==========================================
# 3. Delhi area
# ==========================================

bbox = BBox(
    bbox=[77.15, 28.55, 77.28, 28.68],
    crs=CRS.WGS84
)


# ==========================================
# 4. Function to download true-color image
# ==========================================

def get_true_color(start_date, end_date):

    evalscript = """
    //VERSION=3

    function setup() {

        return {
            input: [
                {
                    bands: ["B02", "B03", "B04"],
                    units: "REFLECTANCE"
                }
            ],

            output: {
                bands: 3,
                sampleType: "AUTO"
            }
        };
    }

    function evaluatePixel(sample) {

        return [
            2.5 * sample.B04,
            2.5 * sample.B03,
            2.5 * sample.B02
        ];
    }
    """

    request = SentinelHubRequest(

        evalscript=evalscript,

        input_data=[
            SentinelHubRequest.input_data(
                data_collection=sentinel2,
                time_interval=(start_date, end_date),
                mosaicking_order="leastCC"
            )
        ],

        responses=[
            SentinelHubRequest.output_response(
                "default",
                MimeType.PNG
            )
        ],

        bbox=bbox,

        size=(650, 650),

        config=config
    )

    images = request.get_data()

    if len(images) == 0:
        raise Exception(
            f"No satellite image found for {start_date} to {end_date}"
        )

    return images[0]


# ==========================================
# 5. Download 2020 satellite image
# ==========================================

print()
print("Downloading 2020 satellite image...")

image_2020 = get_true_color(
    "2020-01-01",
    "2020-01-31"
)

print("2020 image received.")


# ==========================================
# 6. Download 2025 satellite image
# ==========================================

print()
print("Downloading 2025 satellite image...")

image_2025 = get_true_color(
    "2025-01-01",
    "2025-01-31"
)

print("2025 image received.")


# ==========================================
# 7. Save 2020 image
# ==========================================

plt.figure(figsize=(9, 9))

plt.imshow(image_2020)

plt.title(
    "Delhi Satellite Image — 2020"
)

plt.axis("off")

plt.tight_layout()

plt.savefig(
    "delhi_2020_true_color.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ==========================================
# 8. Save 2025 image
# ==========================================

plt.figure(figsize=(9, 9))

plt.imshow(image_2025)

plt.title(
    "Delhi Satellite Image — 2025"
)

plt.axis("off")

plt.tight_layout()

plt.savefig(
    "delhi_2025_true_color.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ==========================================
# 9. NDBI + NDVI + SCL
# ==========================================

analysis_evalscript = """
//VERSION=3

function setup() {

    return {

        input: [
            {
                bands: ["B04", "B08", "B11", "SCL"],
                units: "DN"
            }
        ],

        output: {
            bands: 3,
            sampleType: "FLOAT32"
        }
    };
}


function evaluatePixel(sample) {

    // Invalid / cloud / shadow / water / snow pixels

    if (
        sample.SCL == 0 ||
        sample.SCL == 1 ||
        sample.SCL == 3 ||
        sample.SCL == 6 ||
        sample.SCL == 7 ||
        sample.SCL == 8 ||
        sample.SCL == 9 ||
        sample.SCL == 10 ||
        sample.SCL == 11
    ) {

        return [0, 0, 0];

    }


    // NDBI

    let ndbi_denominator =
        sample.B11 + sample.B08;


    // NDVI

    let ndvi_denominator =
        sample.B08 + sample.B04;


    if (
        ndbi_denominator == 0 ||
        ndvi_denominator == 0
    ) {

        return [0, 0, 0];

    }


    let ndbi =
        (sample.B11 - sample.B08) /
        ndbi_denominator;


    let ndvi =
        (sample.B08 - sample.B04) /
        ndvi_denominator;


    return [
        ndbi,
        ndvi,
        1
    ];

}
"""


# ==========================================
# 10. Download analysis data
# ==========================================

def get_analysis_data(start_date, end_date):

    request = SentinelHubRequest(

        evalscript=analysis_evalscript,

        input_data=[
            SentinelHubRequest.input_data(
                data_collection=sentinel2,
                time_interval=(start_date, end_date),
                mosaicking_order="leastCC"
            )
        ],

        responses=[
            SentinelHubRequest.output_response(
                "default",
                MimeType.TIFF
            )
        ],

        bbox=bbox,

        size=(650, 725),

        config=config
    )

    images = request.get_data()

    if len(images) == 0:
        raise Exception("No analysis data found.")

    return images[0]


# ==========================================
# 11. Get analysis data
# ==========================================

print()
print("Downloading analysis data...")

data_2020 = get_analysis_data(
    "2020-01-01",
    "2020-01-31"
)

data_2025 = get_analysis_data(
    "2025-01-01",
    "2025-01-31"
)

print("Analysis data received.")


# ==========================================
# 12. Extract values
# ==========================================

ndbi_2020 = data_2020[:, :, 0]

ndvi_2020 = data_2020[:, :, 1]

valid_2020 = data_2020[:, :, 2] == 1


ndbi_2025 = data_2025[:, :, 0]

ndvi_2025 = data_2025[:, :, 1]

valid_2025 = data_2025[:, :, 2] == 1


# ==========================================
# 13. Pixels valid in both years
# ==========================================

valid_pixels = (
    valid_2020 &
    valid_2025
)


# ==========================================
# 14. Calculate NDBI change
# ==========================================

ndbi_change = np.full(
    ndbi_2020.shape,
    np.nan,
    dtype=np.float32
)

ndbi_change[valid_pixels] = (
    ndbi_2025[valid_pixels]
    -
    ndbi_2020[valid_pixels]
)


# ==========================================
# 15. Detect potential expansion
# ==========================================

change_threshold = 0.15

minimum_2025_ndbi = 0.05

maximum_2025_ndvi = 0.35


potential_expansion = (

    valid_pixels

    &

    (ndbi_change > change_threshold)

    &

    (ndbi_2025 > minimum_2025_ndbi)

    &

    (ndvi_2025 < maximum_2025_ndvi)

)


# ==========================================
# 16. Remove small isolated regions
# ==========================================

labeled_array, number_of_regions = ndimage.label(
    potential_expansion
)


region_sizes = np.bincount(
    labeled_array.ravel()
)


minimum_region_pixels = 5


clean_expansion = np.zeros_like(
    potential_expansion,
    dtype=bool
)


for region_id in range(
    1,
    number_of_regions + 1
):

    if (
        region_sizes[region_id]
        >= minimum_region_pixels
    ):

        clean_expansion[
            labeled_array == region_id
        ] = True


# ==========================================
# 17. Calculate area
# ==========================================

pixel_area_m2 = 20 * 20

changed_pixels = np.sum(
    clean_expansion
)

changed_area_m2 = (
    changed_pixels *
    pixel_area_m2
)

changed_area_km2 = (
    changed_area_m2 /
    1_000_000
)


# ==========================================
# 18. Save NDBI change map
# ==========================================

plt.figure(figsize=(9, 9))

plt.imshow(
    ndbi_change,
    cmap="RdYlBu_r",
    vmin=-0.5,
    vmax=0.5
)

plt.colorbar(
    label="NDBI Change"
)

plt.title(
    "Delhi NDBI Change — 2020 → 2025"
)

plt.axis("off")

plt.tight_layout()

plt.savefig(
    "delhi_clean_change_map.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ==========================================
# 19. Save expansion-only map
# ==========================================

plt.figure(figsize=(9, 9))

plt.imshow(
    clean_expansion,
    cmap="Reds"
)

plt.title(
    "Potential Built-up Expansion — Delhi 2020 → 2025"
)

plt.axis("off")

plt.tight_layout()

plt.savefig(
    "delhi_expansion_map.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ==========================================
# 20. Create clear satellite + expansion overlay
# ==========================================

# Resize the analysis mask to match the
# satellite image.

mask_resized = ndimage.zoom(
    clean_expansion.astype(np.uint8),
    (
        image_2025.shape[0] / clean_expansion.shape[0],
        image_2025.shape[1] / clean_expansion.shape[1]
    ),
    order=0
)

# Make sure dimensions match exactly.

mask_resized = mask_resized[
    :image_2025.shape[0],
    :image_2025.shape[1]
]

# Create a copy of the satellite image.

overlay_image = image_2025.copy()


# ==========================================
# Make detected areas bright red
# ==========================================

# Find detected pixels.

detected = mask_resized == 1


# Blend the detected pixels with bright red.

overlay_image[detected, 0] = 255

overlay_image[detected, 1] = (
    overlay_image[detected, 1] * 0.25
)

overlay_image[detected, 2] = (
    overlay_image[detected, 2] * 0.25
)


# ==========================================
# Create final image
# ==========================================

plt.figure(figsize=(10, 10))

plt.imshow(
    overlay_image
)

plt.title(
    "Potential Built-up Expansion\n"
    "Delhi 2020 → 2025"
)

plt.axis("off")

plt.tight_layout()

plt.savefig(
    "delhi_expansion_overlay.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ==========================================
# Also create a change map with boundaries
# ==========================================

plt.figure(figsize=(10, 10))

plt.imshow(
    image_2025
)

# Find boundaries of detected regions.

boundary = (
    ndimage.binary_dilation(detected)
    &
    ~detected
)

plt.imshow(
    np.ma.masked_where(
        ~boundary,
        boundary
    ),
    cmap="Reds",
    alpha=1.0
)

plt.title(
    "Potential Expansion Zones\n"
    "Delhi 2020 → 2025"
)

plt.axis("off")

plt.tight_layout()

plt.savefig(
    "delhi_expansion_boundary.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()

# ==========================================
# 21. Save numerical mask
# ==========================================

np.save(
    "potential_expansion.npy",
    clean_expansion
)


# ==========================================
# 22. Print final results
# ==========================================

print()
print("==========================================")
print("       SATELLITE CHANGE ANALYSIS")
print("==========================================")

print()

print(
    "Valid pixels:",
    int(np.sum(valid_pixels))
)

print(
    "Potential expansion pixels:",
    int(changed_pixels)
)

print(
    "Approximate potential changed area:",
    round(changed_area_km2, 3),
    "km²"
)

print()

print("Files created:")

print("1. delhi_2020_true_color.png")

print("2. delhi_2025_true_color.png")

print("3. delhi_clean_change_map.png")

print("4. delhi_expansion_map.png")

print("5. delhi_expansion_overlay.png")

print("6. potential_expansion.npy")

print()

print("Analysis complete!")