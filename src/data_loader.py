"""
data_loader.py
โมดูลสำหรับโหลด ตรวจสอบความถูกต้อง (Validation) และจัดเตรียมข้อมูลสำหรับ Dashboard เวอร์ชัน 2.0
รองรับ 9 กลุ่มปัญหา, 6 ภูมิภาค, ข้อมูลเสริมจริง และขอบเขตแผนที่ GeoJSON 77 จังหวัด
"""

import json
import os
import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CLEAN_GROUPED_CSV_PATH = os.path.join(DATA_DIR, "data_clean_grouped_region.csv")
PROVINCE_CSV_PATH = os.path.join(DATA_DIR, "dashboard_province_data.csv")
MAIN_OLD_CSV_PATH = os.path.join(DATA_DIR, "dashboard_main_data.csv")
GEOJSON_PATH = os.path.join(DATA_DIR, "thailand_provinces.geojson")


@st.cache_data(show_spinner="กำลังโหลดและตรวจสอบข้อมูลเวอร์ชันล่าสุด...")
def load_all_data():
    """
    โหลดข้อมูล CSV ชุดใหม่ (9 กลุ่มปัญหา) และข้อมูลเสริมระดับจังหวัด พร้อมตรวจสอบความถูกต้อง
    """
    if not os.path.exists(CLEAN_GROUPED_CSV_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ข้อมูลหลักใหม่: {CLEAN_GROUPED_CSV_PATH}")
    if not os.path.exists(PROVINCE_CSV_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ข้อมูลเสริม: {PROVINCE_CSV_PATH}")
    if not os.path.exists(GEOJSON_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ GeoJSON: {GEOJSON_PATH}")

    # โหลดไฟล์ CSV หลักใหม่ (470 แถว, 9 คอลัมน์)
    main_df = pd.read_csv(CLEAN_GROUPED_CSV_PATH, encoding="utf-8-sig")

    # โหลดไฟล์ข้อมูลเสริมระดับจังหวัด (154 แถว)
    province_df = pd.read_csv(PROVINCE_CSV_PATH, encoding="utf-8-sig")

    # โหลดไฟล์ GeoJSON ขอบเขต 77 จังหวัด
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # QA Assertions ตามข้อกำหนดใน BRD v2.0 & HANDOFF v2.0
    assert main_df.shape == (470, 9), f"main_df shape ผิดพลาด: {main_df.shape}"
    assert province_df.shape == (154, 8), f"province_df shape ผิดพลาด: {province_df.shape}"
    assert (main_df["region"] == "ทั่วประเทศ").sum() == 6, "แถวทั่วประเทศใน main_df ไม่เท่ากับ 6 แถว"
    
    # ตรวจสอบ 77 จังหวัดในแต่ละปี
    prov_counts = province_df.groupby("year")["region"].nunique().to_dict()
    assert prov_counts == {2566: 77, 2567: 77}, f"จำนวนจังหวัดรายปีผิด: {prov_counts}"
    assert not province_df.duplicated(["year", "region"]).any(), "พบแถวซ้ำ (year, region) ใน province_df"

    # ตรวจสอบค่าว่างของตัวชี้วัดเสริมปี 2566
    p66 = province_df[province_df["year"] == 2566]
    assert p66[["monthly_expenditure", "rice_yield_per_rai"]].isna().all().all(), "ปี 2566 ต้องไม่มีค่าใช้จ่ายและผลผลิตข้าว"
    assert province_df["unemployment_rate"].notna().all(), "อัตราการว่างงานต้องมีครบทุกจังหวัดทั้ง 2 ปี"

    # ตรวจสอบจำนวน 77 จังหวัดจริงใน main_df (ไม่รวมแถว 'ทั่วประเทศ')
    main_provs = main_df[main_df["region"] != "ทั่วประเทศ"]["region"].nunique()
    assert main_provs == 77, f"จำนวนจังหวัดใน main_df ไม่เท่ากับ 77: {main_provs}"

    # ตรวจสอบกลุ่มปัญหาครบ 9 กลุ่ม
    groups_9 = main_df["Iss_Need_Grouped"].dropna().unique().tolist()
    assert len(groups_9) == 9, f"จำนวนกลุ่มปัญหาใน main_df ไม่เท่ากับ 9: {len(groups_9)}"

    # ตรวจสอบภูมิภาคครบ 6 ภูมิภาค (ไม่นับทั่วประเทศ)
    regions = [r for r in main_df["region_group"].dropna().unique() if r != "ทั่วประเทศ"]
    assert len(regions) == 6, f"จำนวนภูมิภาคไม่เท่ากับ 6: {len(regions)}"

    # สร้าง Dictionary การจับคู่ระหว่างจังหวัดกับภูมิภาค (Region mapping)
    region_mapping = (
        main_df[main_df["region"] != "ทั่วประเทศ"]
        .drop_duplicates("region")
        .set_index("region")["region_group"]
        .to_dict()
    )
    # เพิ่มภูมิภาคลงใน province_df เพื่อความสะดวกในการวิเคราะห์
    province_df["region_group"] = province_df["region"].map(region_mapping)

    return main_df, province_df, geojson_data


def get_provinces_list(province_df):
    """ส่งคืนรายชื่อจังหวัด 77 จังหวัด เรียงตามลำดับตัวอักษรไทย"""
    return sorted(province_df["region"].unique().tolist())


def get_region_groups_list(main_df):
    """ส่งคืนรายชื่อ 6 ภูมิภาคมาตรฐาน (ไม่รวมแถว 'ทั่วประเทศ')"""
    regs = main_df[main_df["region"] != "ทั่วประเทศ"]["region_group"].dropna().unique().tolist()
    return sorted(regs)


def get_problem_groups_9(main_df):
    """ส่งคืนรายชื่อ 9 กลุ่มปัญหามาตรฐานจากชุดข้อมูลใหม่"""
    return sorted(main_df["Iss_Need_Grouped"].dropna().unique().tolist())


def get_subproblems(main_df, group=None, year=None):
    """ส่งคืนรายการปัญหาย่อย (Iss_Need) ตามกลุ่มปัญหาและ/หรือปี"""
    filtered = main_df[main_df["region"] != "ทั่วประเทศ"]
    if group:
        filtered = filtered[filtered["Iss_Need_Grouped"] == group]
    if year:
        filtered = filtered[filtered["year"] == year]
    return sorted(filtered["Iss_Need"].dropna().unique().tolist())
