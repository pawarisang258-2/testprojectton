"""
data_loader.py
โมดูลสำหรับโหลด ตรวจสอบความถูกต้อง (Validation) และจัดเตรียมข้อมูลสำหรับ Dashboard
"""

import json
import os
import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
MAIN_CSV_PATH = os.path.join(DATA_DIR, "dashboard_main_data.csv")
PROVINCE_CSV_PATH = os.path.join(DATA_DIR, "dashboard_province_data.csv")
COMPARISON_CSV_PATH = os.path.join(DATA_DIR, "dashboard_comparison.csv")
GEOJSON_PATH = os.path.join(DATA_DIR, "thailand_provinces.geojson")


@st.cache_data(show_spinner="กำลังโหลดและตรวจสอบข้อมูล...")
def load_all_data():
    """
    โหลดข้อมูล CSV 3 ไฟล์ และไฟล์ GeoJSON พร้อมตรวจสอบ Schema ตาม Acceptance Criteria
    """
    if not os.path.exists(MAIN_CSV_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์: {MAIN_CSV_PATH}")
    if not os.path.exists(PROVINCE_CSV_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์: {PROVINCE_CSV_PATH}")
    if not os.path.exists(COMPARISON_CSV_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์: {COMPARISON_CSV_PATH}")
    if not os.path.exists(GEOJSON_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ GeoJSON: {GEOJSON_PATH}")

    # โหลดไฟล์ CSV
    main_df = pd.read_csv(MAIN_CSV_PATH, encoding="utf-8-sig")
    province_df = pd.read_csv(PROVINCE_CSV_PATH, encoding="utf-8-sig")
    comparison_df = pd.read_csv(COMPARISON_CSV_PATH, encoding="utf-8-sig")

    # โหลดไฟล์ GeoJSON
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # QA Assertions ตามข้อกำหนดใน HANDOFF.md
    assert main_df.shape == (470, 12), f"main_df shape ผิดพลาด: {main_df.shape}"
    assert province_df.shape == (154, 8), f"province_df shape ผิดพลาด: {province_df.shape}"
    assert comparison_df.shape == (8, 6), f"comparison_df shape ผิดพลาด: {comparison_df.shape}"
    assert (main_df["region"] == "ทั่วประเทศ").sum() == 6, "แถวทั่วประเทศใน main_df ไม่เท่ากับ 6 แถว"
    
    # ตรวจสอบ 77 จังหวัดในแต่ละปี
    prov_counts = province_df.groupby("year")["region"].nunique().to_dict()
    assert prov_counts == {2566: 77, 2567: 77}, f"จำนวนจังหวัดรายปีผิด: {prov_counts}"
    assert not province_df.duplicated(["year", "region"]).any(), "พบแถวซ้ำ (year, region) ใน province_df"

    # ตรวจสอบค่าว่างของตัวชี้วัดเสริมปี 2566
    p66 = province_df[province_df["year"] == 2566]
    assert p66[["monthly_expenditure", "rice_yield_per_rai"]].isna().all().all(), "ปี 2566 ต้องไม่มีค่าใช้จ่ายและผลผลิตข้าว"
    assert province_df["unemployment_rate"].notna().all(), "อัตราการว่างงานต้องมีครบทุกจังหวัดทั้ง 2 ปี"

    # ตรวจสอบจำนวนจังหวัดใน main_df (ไม่รวมทั่วประเทศ)
    main_provs = main_df[main_df["region"] != "ทั่วประเทศ"]["region"].nunique()
    assert main_provs == 77, f"จำนวนจังหวัดใน main_df ไม่เท่ากับ 77: {main_provs}"

    return main_df, province_df, comparison_df, geojson_data


def get_provinces_list(province_df):
    """ส่งคืนรายชื่อจังหวัด 77 จังหวัด เรียงตามลำดับตัวอักษรไทย"""
    return sorted(province_df["region"].unique().tolist())


def get_problem_groups(main_df):
    """ส่งคืนรายชื่อ 6 กลุ่มปัญหามาตรฐาน"""
    return sorted(main_df["problem_group"].dropna().unique().tolist())


def get_subproblems_by_group(main_df, group=None, year=None):
    """ส่งคืนรายการปัญหาย่อย (standard_problem) ตามกลุ่มปัญหาและ/หรือปี"""
    filtered = main_df[main_df["region"] != "ทั่วประเทศ"]
    if group:
        filtered = filtered[filtered["problem_group"] == group]
    if year:
        filtered = filtered[filtered["year"] == year]
    return sorted(filtered["standard_problem"].dropna().unique().tolist())
