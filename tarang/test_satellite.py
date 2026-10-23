import os
from dotenv import load_dotenv

from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    DataCollection,
    MimeType,
    BBox,
    CRS,
)

from PIL import Image

load_dotenv()

# -----------------------------
# 1. Copernicus credentials
# -----------------------------

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


# -----------------------------
# 2. Delhi area
# -----------------------------

bbox = BBox(
    bbox=[77.15, 28.55, 77.28, 28.68],
    crs=CRS.WGS84
)


# -----------------------------
# 3. RGB satellite image
# -----------------------------

evalscript = """
//VERSION=3

function setup() {
    return {
        input: ["B02", "B03", "B04"],
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


# -----------------------------
# 4. Function to download image
# -----------------------------

def download_image(start_date, end_date, filename):

    print(f"Downloading image for {start_date} to {end_date}...")

    request = SentinelHubRequest(

        evalscript=evalscript,

        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                    "s2l2a",
                    service_url=config.sh_base_url
                ),

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

        size=(800, 800),

        config=config
    )

    images = request.get_data()

    print("Images received:", len(images))

    if len(images) > 0:

        Image.fromarray(images[0]).save(filename)

        print("Saved:", filename)

    else:

        print("No image found.")


# -----------------------------
# 5. Download 2020 image
# -----------------------------

download_image(
    "2020-01-01",
    "2020-01-31",
    "delhi_2020.png"
)


# -----------------------------
# 6. Download 2025 image
# -----------------------------

download_image(
    "2025-01-01",
    "2025-01-31",
    "delhi_2025.png"
)


print()
print("DONE!")
print("2020 image: delhi_2020.png")
print("2025 image: delhi_2025.png")