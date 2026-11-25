"""Shared input and output paths, anchored to the repository root."""

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA = DATA_DIR / "07earthquake.csv"
BOUNDARIES_DIR = DATA_DIR / "boundaries"
COUNTRY_BOUNDARIES = BOUNDARIES_DIR / "ne_50m_admin_0_countries.zip"
PROVINCE_BOUNDARIES = BOUNDARIES_DIR / "ne_10m_admin_1_states_provinces.zip"

TABLES_DIR = ROOT_DIR / "results" / "tables"
FIGURES_DIR = ROOT_DIR / "results" / "figures"
