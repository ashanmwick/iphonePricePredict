# Phone Price Prediction (Sri Lanka Market)

Machine learning project for predicting mobile phone prices (LKR) from listing attributes such as condition, brand, RAM, memory, SIM support, and network.

The repository includes:
- Data collection scripts (AdListing Site listing links + ad detail scraping)
- Data cleaning and model training notebooks
- Saved Random Forest model artifacts
- A Streamlit web app for inference

---

## Current Project Status

- ✅ End-to-end pipeline is present: scrape → clean → train → serve
- ✅ Trained model artifacts exist in `models/`
- ✅ Streamlit app is ready in `main.py`

---

## Repository Structure

```text
iphonePricePredict/
├── main.py                          # Streamlit inference app
├── requirements.txt                 # Project dependencies
├── Scripts/
│   ├── getlink.py                   # Harvest ad links from Adlisting Site
│   └── scrape.py                    # Scrape ad details into CSV
├── data/
│   ├── phone-ad-links/
│   │   └── phone.txt                # Collected ad URLs
│   ├── phone-details/
│   │   ├── phone_dataset.csv        # Raw structured scrape output
│   │   ├── cleaned_my_dataset.csv   # Model-ready cleaned dataset
│   │   └── old/                     # Legacy datasets
│   └── failed-links/
│       ├── iphone_failed_links.txt
│       └── phone_failed_links.txt
├── models/
│   ├── random_forest_phone_price_model.pkl
│   ├── feature_names.json
│   ├── model_metadata.json
│   └── evaluation_metrics.json
├── notebooks/
│   ├── noteBook.ipynb               # Main preprocessing + training notebook
│   └── dataset_analytics_for_hyper_para.ipynb      # Additional analysis notebook for hyper parameter 
└── webPage/                         # Empty at the moment
```

---

## How the Pipeline Works

### 1) Link Harvesting
`Scripts/getlink.py`:
- Launches Chrome through `undetected_chromedriver`
- Visits ikman mobile-phone listing pages
- Collects ad URLs from anchor tags with class `gtm-ad-item`
- Writes unique links to `data/phone-ad-links/phone.txt`

### 2) Ad Detail Scraping
`Scripts/scrape.py`:
- Reads all `*.txt` files from `data/phone-ad-links/`
- Fetches each ad page with retry + timeout handling
- Dynamically extracts metadata blocks (label/value pairs)
- Extracts `Price`, `Features`, and `Description`
- Saves structured CSV to `data/phone-details/phone_dataset.csv`
- Saves failed URLs to `data/failed-links/phone_failed_links.txt`

### 3) Cleaning + Feature Engineering
`notebooks/noteBook.ipynb`:
- Loads `data/phone-details/phone_dataset.csv`
- Imputes missing values:
	- `Network`, `SIM Support` via per-model mode (fallback to global mode)
	- `RAM`, `Memory` via per-model median (fallback to global median)
- Normalizes RAM/Memory numeric values
- Consolidates rare brands into `Other brand`
- Drops high-cardinality / noisy columns (e.g., `Model`, `Description`, `Features`, etc.)
- Saves cleaned data to `data/phone-details/cleaned_my_dataset.csv`
- Applies one-hot encoding with `pd.get_dummies`

### 4) Model Training
`notebooks/noteBook.ipynb`:
- Model: `RandomForestRegressor`
- Key params: `n_estimators=100`, `max_depth=15`, `min_samples_split=5`, `random_state=42`
- Train/test split used in notebook: `test_size=0.25`

### 5) Model Persistence
Generated artifacts in `models/`:
- `random_forest_phone_price_model.pkl`
- `feature_names.json`
- `model_metadata.json`
- `evaluation_metrics.json`

### 6) Inference App
`main.py` (Streamlit):
- Loads model + feature list from `models/`
- Builds UI for: Condition, Brand, RAM, Memory, SIM Support, Network
- Constructs one-hot encoded input vector aligned to `feature_names.json`
- Predicts and displays price in LKR

---

## Model Snapshot (from current artifacts)

From `models/evaluation_metrics.json` and `models/model_metadata.json`:

- R²: **0.8207** (~82.07%)
- MAE: **LKR 19,360.26**
- RMSE: **LKR 30,038.62**
- Training samples: **779**
- Testing samples: **260**
- Features used: **19**
- Trained date: **2026-02-23 15:39:06**

> Note: Notebook cells may contain exploratory runs; treat JSON artifacts in `models/` as the authoritative latest saved results.

---

## Setup

### Prerequisites
- Python 3.10+ recommended
- Windows PowerShell (or any shell)

### Install dependencies

```bash
pip install -r requirements.txt
```

If you plan to run link harvesting (`Scripts/getlink.py`), install:

```bash
pip install undetected-chromedriver
```

---

## Usage

### Run the Streamlit app

```bash
streamlit run main.py
```

### Re-scrape links

```bash
python Scripts/getlink.py
```

### Re-scrape ad details

```bash
python Scripts/scrape.py
```

### Retrain model

Open and run notebook:
- `notebooks/noteBook.ipynb`

This notebook both trains the model and re-generates files in `models/`.

---

## Input Features Expected by the Deployed Model

The app aligns runtime inputs to this feature set (from `models/feature_names.json`):
- Numeric: `RAM`, `Memory`
- Condition: `Brand New`, `Used`
- Brand: `Apple`, `Google`, `Honor`, `Huawei`, `Oppo`, `Other brand`, `Samsung`, `Vivo`, `Xiaomi`
- SIM Support: `Dual SIM`, `Dual VoLTE`, `Single SIM`
- Network: `4G`, `5G`, `VoLTE`

---
