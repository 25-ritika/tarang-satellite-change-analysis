# Tarang — Satellite Imagery Change Analysis

Tarang is an interactive Python application for exploring landscape changes using multi-temporal satellite imagery. It uses Sentinel-2 imagery and spectral indices to visualize changes in vegetation and built-up areas.

## Features

- Retrieve satellite imagery using Sentinel Hub.
- Compare satellite images across different time periods.
- Analyze vegetation using NDVI (Normalized Difference Vegetation Index).
- Analyze built-up signals using NDBI (Normalized Difference Built-up Index).
- Visualize potential changes through generated maps.
- Explore results using an interactive Streamlit interface.

## Technology Stack

- Python
- Streamlit
- Sentinel Hub
- NumPy
- SciPy
- Pillow
- Requests
- python-dotenv

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/25-ritika/tarang-satellite-change-analysis.git
cd tarang-satellite-change-analysis
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Sentinel Hub

Create a local `.env` file containing the credentials required by your application. Never publish your credentials or `.env` file.

### 5. Run Tarang

```bash
streamlit run app.py
```

## How It Works

1. Select or query a study location.
2. Retrieve satellite imagery for the selected time periods.
3. Process the imagery and calculate spectral indices.
4. Generate visualizations highlighting potential landscape changes.
5. Explore the outputs through the Streamlit application.

## Limitations

Tarang is an evolving prototype. Clouds, shadows, seasonal differences, and imagery quality can affect the results. NDVI and NDBI are indicators, not definitive proof of land-cover change. Further validation against reference data is needed.

## Future Improvements

- Cloud and cloud-shadow masking.
- Improved multi-temporal image preprocessing.
- Quantitative accuracy evaluation.
- Support for more study areas and time periods.
- Improved geospatial visualization and reporting.

## Acknowledgements

- [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/)
- [Sentinel Hub](https://www.sentinel-hub.com/)
- [Streamlit](https://streamlit.io/)
