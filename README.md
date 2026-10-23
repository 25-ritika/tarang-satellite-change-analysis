# Tarang — Satellite Imagery Change Analysis

**Explore landscape changes through multi-temporal satellite imagery.**

Tarang is an interactive geospatial analysis application built with Python and Streamlit. It retrieves Sentinel-2 satellite imagery and analyzes changes in vegetation and built-up signals across different locations and time periods.

[**Live Demo**](https://tarang-satellite-change-analysis-akdiayhfthoovsfyqfsbjk.streamlit.app/)**&#x20;· [GitHub Repository](https://github.com/25-ritika/tarang-satellite-change-analysis)**

## Overview

Urban expansion and vegetation changes are important factors in sustainable urban planning and environmental monitoring. Tarang provides an interactive workflow for exploring these changes through satellite imagery, spectral indices, and image-processing techniques.

The application supports location-oriented queries, satellite imagery retrieval, multi-temporal comparison, and visualization of potential changes.

## Features

- **Satellite imagery retrieval:** Retrieve Sentinel-2 Level-2A imagery through Sentinel Hub.
- **Multi-temporal analysis:** Compare imagery from different time periods.
- **Natural-language queries:** Parse supported queries describing a location and change-analysis period.
- **NDVI analysis:** Explore vegetation-related spectral patterns.
- **NDBI analysis:** Explore built-up-related spectral patterns.
- **Change visualization:** Generate maps highlighting potential changes.
- **Interactive dashboard:** Explore analysis results through a Streamlit interface.

## Live Application Results

The deployed application displayed the following results for a sample analysis of Kashmere Gate, Delhi, for 2020–2025.

| Metric                 | Displayed result |
| ---------------------- | ---------------: |
| Potential changed area |        1.599 km² |
| Study area changed     |            5.88% |
| Change zones           |               91 |
| Largest zone           |        1.373 km² |

These figures are outputs from the current prototype. They have not been independently validated against ground-truth data and should not be interpreted as confirmed measurements of urban expansion.

## Screenshots

### Satellite imagery comparison

| Delhi — 2020 | Delhi — 2025 |
| ------------ | ------------ |
|              |              |

### Change detection map



## Technology Stack

- **Language:** Python
- **Interface:** Streamlit
- **Satellite imagery:** Sentinel Hub and Sentinel-2 Level-2A
- **Numerical analysis:** NumPy
- **Image processing:** SciPy and Pillow
- **HTTP requests:** Requests
- **Configuration:** python-dotenv

## How It Works

1. The user enters or selects a study location and time period.
2. The application interprets the query and prepares the satellite imagery request.
3. Sentinel Hub provides imagery for the requested study area and dates.
4. The application processes imagery and uses spectral indices such as NDVI and NDBI.
5. Image-processing methods help identify and visualize potential changes.
6. Results are presented through an interactive dashboard.

## Run Locally

### Prerequisites

- Python installed on your system
- A Sentinel Hub account with appropriate data access
- The credentials required by the application

### 1. Clone the repository

```bash
git clone https://github.com/25-ritika/tarang-satellite-change-analysis.git
cd tarang-satellite-change-analysis
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

Create a local `.env` file using the exact environment-variable names expected by the application. Never upload this file or expose your credentials publicly.

For deployment, configure the required values through Streamlit Community Cloud Secrets.

### 5. Start the application

```bash
streamlit run app.py
```

## Understanding the Indices

**Normalized Difference Vegetation Index (NDVI)** helps examine vegetation patterns using red and near-infrared reflectance.

**Normalized Difference Built-up Index (NDBI)** helps highlight built-up signals using shortwave-infrared and near-infrared reflectance.

These indices are indicators rather than definitive land-cover classifications. Their interpretation depends on image quality, seasonality, atmospheric conditions, and other factors.

## Limitations

- Clouds, haze, shadows, and image quality may affect results.
- Differences in acquisition dates and seasons can influence index values.
- Threshold-based change detection can produce false positives.
- The displayed area estimates require further validation against reference data.
- The current prototype uses numerical analysis and image-processing techniques; it does not depend on a separately trained machine-learning model.

## Future Improvements

- [ ] Improve cloud and cloud-shadow masking.
- [ ] Improve image normalization across time periods.
- [ ] Validate change estimates against reference datasets.
- [ ] Improve geospatial visualization and area calculations.
- [ ] Add automated tests and error handling.
- [ ] Support additional locations and time periods.
- [ ] Add downloadable analysis reports.

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Submit a pull request describing the changes.

Please open an issue before making major changes.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

- [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/)
- [Sentinel Hub](https://www.sentinel-hub.com/)
- [Streamlit](https://streamlit.io/)

---

**Tarang — Exploring landscape change through satellite imagery.**
