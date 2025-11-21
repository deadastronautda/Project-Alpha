🌍 Russian version: [README.md](README.md)

# 📊 Project Alpha — Financial Statement Analyzer

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-brightgreen.svg)
![Tests](https://img.shields.io/badge/Tests-PyTest-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![CI](https://img.shields.io/badge/GitHub-Actions-blue.svg)

**Project Alpha** is an interactive Streamlit application designed to analyze financial statements uploaded as Excel files.
It performs:

* 📈 Horizontal financial analysis
* 📉 Vertical structural analysis
* 🔍 Anomaly detection
* 🧮 Financial ratio calculation
* 📊 Interactive Plotly visualizations
* 📄 Automatic PDF report generation
* 📥 CSV export
* 📅 Year-by-year financial breakdown

The app supports flat Excel formats for easy preprocessing and model building.

---

# 🚀 Features

### 🔎 Data Analysis

* Multi-year horizontal comparison
* Vertical structural decomposition
* Liquidity, profitability, and financial stability metrics
* Trend insights

### ⚠️ Anomaly Detection

* Statistical anomalies (Z-score outliers)
* Logical inconsistencies (e.g., revenue growth + profit drop)
* Liquidity risk detection
* Abnormal receivables and payables growth

### 📊 Visualization

* Trend charts
* Ratio vs. normative benchmarks
* Pie charts for asset structure

### 📄 Exports

* Auto-generated PDF report
* Raw CSV export
* Downloadable visual results

---

# 📁 Project Structure

```
Project-Alpha/
│
├── app.py                 
├── financial_data_flat.xlsx
├── requirements.txt
├── Dockerfile
│
├── tests/                 
│   ├── test_app.py
│   ├── test_smoke.py
│   ├── test_streamlit_ui.py
│   └── conftest.py
│
├── .github/workflows/tests.yml
│
├── run_app.bat
├── run_tests.bat
└── README.md / README.en.md
```

---

# 🧑‍💻 Local Installation & Usage

## 1️⃣ Create virtual environment

```powershell
python -m venv venv
```

## 2️⃣ Activate it

```powershell
.\venv\Scripts\activate
```

## 3️⃣ Install dependencies

```powershell
pip install -r requirements.txt
```

## 4️⃣ Launch the app

```powershell
streamlit run app.py
```

Open:

```
http://localhost:8501/
```

## ❌ Stop Streamlit server

```
CTRL + C
Y
```

---

# 🐳 Docker Usage

## 1️⃣ Build the container

```bash
docker build -t project-alpha .
```

## 2️⃣ Run the container

```bash
docker run -p 8501:8501 project-alpha
```

Visit:

```
http://localhost:8501/
```

## ❌ Stop Docker container

```bash
docker ps
docker stop <container_id>
```

---

# 🧪 Running Tests

The project includes a complete PyTest suite covering:

* Data loading
* Preprocessing
* Ratio calculations
* Horizontal & vertical analysis
* Anomaly detection
* Streamlit smoke tests

All test scripts are located in the `tests/` directory.

---

## ▶️ Run tests locally

### 1. Activate virtual environment

```powershell
.\venv\Scripts\activate
```

### 2. Install test dependencies

```powershell
pip install pytest pytest-cov
```

### 3. Run all tests

```powershell
pytest
```

### 4. Run with coverage

```powershell
pytest --cov=app --cov-report=term-missing
```

### 5. Alternative script

```powershell
.\run_tests.bat
```

---

# ⚙️ Continuous Integration (GitHub Actions)

The CI workflow is located at:

```
.github/workflows/tests.yml
```

It automatically runs:

* Python setup
* Dependency installation
* Full PyTest suite
* Coverage report

### CI triggers:

* every `git push`
* every Pull Request into `main`

### Results:

Go to GitHub repo → **Actions** tab
You’ll see “Run Tests” workflow with logs, coverage, and error traces.

---

# 📷 Screenshots (example)

### Dashboard

![screenshot](https://via.placeholder.com/900x400?text=Main+Dashboard)

### Ratios

![screenshot](https://via.placeholder.com/900x400?text=Financial+Ratios)

---

# 📜 License

Distributed under the **MIT License**.

---

# 🤝 Author

**Project Alpha** — a professional financial analysis toolkit designed for analysts, researchers, and developers.
