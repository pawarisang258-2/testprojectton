"""
app.py
แอปพลิเคชันหลัก Interactive Dashboard:
การวิเคราะห์ความต้องการให้รัฐบาลช่วยเหลือของหมู่บ้าน/ชุมชนไทย ปี 2566–2567 (Halloween Edition)
เวอร์ชัน 2.1: 3 แท็บหลัก, ธีม Halloween Dark Gothic, ฟอนต์ Prompt, 9 กลุ่มปัญหามาตรฐาน, ข้อมูลจริง 100%
"""

import streamlit as st
import pandas as pd
from src.data_loader import (
    load_all_data,
    get_provinces_list,
    get_region_groups_list,
    get_problem_groups_9
)
from src.theme import CUSTOM_CSS_HALLOWEEN
from src.tab1_overview import render_tab1
from src.tab2_province_reality import render_tab2
from src.tab3_yoy_comparison import render_tab3

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(
    page_title="🎃 Thailand Issues Radar 2566–2567 (Halloween Edition)",
    page_icon="🎃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ฉีด CSS ปรับแต่งสไตล์ Halloween Dark Gothic + Glassmorphism
st.markdown(CUSTOM_CSS_HALLOWEEN, unsafe_allow_html=True)

# 3. โหลดข้อมูลจริง (Cached)
try:
    main_df, province_df, geojson_data = load_all_data()
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
    st.stop()

# 4. ฟังก์ชันจัดการ State ของตัวกรองส่วนกลาง (Global Filter State)
if "filter_year" not in st.session_state:
    st.session_state["filter_year"] = "ทั้งหมด"
if "filter_regions" not in st.session_state:
    st.session_state["filter_regions"] = []
if "filter_provinces" not in st.session_state:
    st.session_state["filter_provinces"] = []
if "filter_groups" not in st.session_state:
    st.session_state["filter_groups"] = []
if "filter_sub_search" not in st.session_state:
    st.session_state["filter_sub_search"] = ""
if "filter_rank" not in st.session_state:
    st.session_state["filter_rank"] = "ทั้งหมด"
if "filter_per_vill" not in st.session_state:
    st.session_state["filter_per_vill"] = (0.0, 100.0)


def reset_all_filters():
    """รีเซ็ตตัวกรองทั้งหมดกลับสู่ค่าเริ่มต้น"""
    st.session_state["filter_year"] = "ทั้งหมด"
    st.session_state["filter_regions"] = []
    st.session_state["filter_provinces"] = []
    st.session_state["filter_groups"] = []
    st.session_state["filter_sub_search"] = ""
    st.session_state["filter_rank"] = "ทั้งหมด"
    st.session_state["filter_per_vill"] = (0.0, 100.0)
    
    local_keys = [
        "t1_map_mode", "t1_map_target_group", "t1_map_target_sub",
        "t2_year_radio", "t2_region_select", "t2_province_dropdown", "quick_pick_province", "t2_reality_indicator",
        "t3_line_reg", "t3_line_group", "t3_shift_radio"
    ]
    for k in local_keys:
        if k in st.session_state:
            del st.session_state[k]


# 5. แถบควบคุมด้านข้าง (Sidebar Controls — ตัวหนังสือคมชัด อ่านง่าย)
with st.sidebar:
    st.markdown("### 🎃 ตัวกรองข้อมูลมัลติมิติ")
    st.caption("ปรับแต่งข้อมูลเพื่อเชื่อมโยงทุกกราฟในแดชบอร์ด")

    if st.button("ล้างตัวกรองทั้งหมด (Reset)", type="secondary", use_container_width=True):
        reset_all_filters()
        st.rerun()

    # 1. ปีที่สำรวจ
    st.session_state["filter_year"] = st.radio(
        "📅 1. เลือกปีการสำรวจ:",
        ["ทั้งหมด", "2567", "2566"],
        index=["ทั้งหมด", "2567", "2566"].index(st.session_state["filter_year"]),
        horizontal=True
    )

    # 2. ภูมิภาค
    all_regs = get_region_groups_list(main_df)
    st.session_state["filter_regions"] = st.multiselect(
        "🏰 2. เลือกภูมิภาค (6 ภาค):",
        options=all_regs,
        default=st.session_state["filter_regions"],
        placeholder="ทุกภูมิภาค"
    )

    # 3. จังหวัด (ค้นหาและเลือกได้หลายจังหวัด)
    available_provs = get_provinces_list(province_df)
    if st.session_state["filter_regions"]:
        prov_in_regs = main_df[main_df["region_group"].isin(st.session_state["filter_regions"])]["region"].unique().tolist()
        available_provs = sorted([p for p in available_provs if p in prov_in_regs])

    st.session_state["filter_provinces"] = st.multiselect(
        "📍 3. เลือกจังหวัด (พิมพ์ค้นหาได้):",
        options=available_provs,
        default=[p for p in st.session_state["filter_provinces"] if p in available_provs],
        placeholder="ทุกจังหวัด (77 จังหวัด)"
    )

    # 4. กลุ่มปัญหา 9 กลุ่ม
    all_groups_9 = get_problem_groups_9(main_df)
    st.session_state["filter_groups"] = st.multiselect(
        "🏷️ 4. กลุ่มปัญหา (ครบ 9 กลุ่ม):",
        options=all_groups_9,
        default=st.session_state["filter_groups"],
        placeholder="ทุกกลุ่มปัญหา"
    )

    # 5. ค้นหาปัญหาย่อย
    st.session_state["filter_sub_search"] = st.text_input(
        "🔍 5. ค้นหาข้อความปัญหาย่อย:",
        value=st.session_state["filter_sub_search"],
        placeholder="พิมพ์คำสำคัญ เช่น ปุ๋ย, น้ำ, หนี้..."
    )

    # 6. อันดับความต้องการ
    rank_options = ["ทั้งหมด", "ความต้องการ อันดับ 1", "ความต้องการ อันดับ 2", "ความต้องการ อันดับ 3"]
    st.session_state["filter_rank"] = st.selectbox(
        "🏆 6. อันดับความต้องการ:",
        options=rank_options,
        index=rank_options.index(st.session_state["filter_rank"])
    )

    # 7. ช่วงร้อยละ Per_vill
    st.session_state["filter_per_vill"] = st.slider(
        "📊 7. ช่วงร้อยละหมู่บ้าน/ชุมชน (Per_vill %):",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state["filter_per_vill"],
        step=1.0
    )

    st.divider()

    # สรุปจำนวนรายการและจังหวัดหลังกรอง
    df_preview = main_df[main_df["region"] != "ทั่วประเทศ"].copy()
    if st.session_state["filter_year"] != "ทั้งหมด":
        df_preview = df_preview[df_preview["year"] == int(st.session_state["filter_year"])]
    if st.session_state["filter_regions"]:
        df_preview = df_preview[df_preview["region_group"].isin(st.session_state["filter_regions"])]
    if st.session_state["filter_provinces"]:
        df_preview = df_preview[df_preview["region"].isin(st.session_state["filter_provinces"])]
    if st.session_state["filter_groups"]:
        df_preview = df_preview[df_preview["Iss_Need_Grouped"].isin(st.session_state["filter_groups"])]
    if st.session_state["filter_sub_search"]:
        df_preview = df_preview[df_preview["Iss_Need"].str.contains(st.session_state["filter_sub_search"], na=False)]
    if st.session_state["filter_rank"] != "ทั้งหมด":
        df_preview = df_preview[df_preview["Need"] == st.session_state["filter_rank"]]
    df_preview = df_preview[
        (df_preview["Per_vill"] >= st.session_state["filter_per_vill"][0]) &
        (df_preview["Per_vill"] <= st.session_state["filter_per_vill"][1])
    ]

    summary_box_html = (
        f"<div style='background:rgba(25, 25, 42, 0.9); padding:12px 14px; border-radius:10px; border:1px solid rgba(138,43,226,0.4); font-size:0.86rem;'>"
        f"<div style='color:#FF9E4A; font-weight:700; margin-bottom:4px;'>⚡ สรุปผลลัพธ์ตัวกรอง:</div>"
        f"<div style='color:#FFFFFF;'>• จำนวนจังหวัด: <b>{df_preview['region'].nunique()}</b> / 77 จังหวัด</div>"
        f"<div style='color:#FFFFFF;'>• รายการความต้องการ: <b>{len(df_preview)}</b> รายการ</div>"
        f"</div>"
    )
    st.markdown(summary_box_html, unsafe_allow_html=True)

    st.divider()

    # ข้อมูลบริบทภาพรวมประเทศ (National Benchmark)
    with st.expander("📌 ข้อมูล 3 อันดับแรกภาพรวมประเทศ", expanded=False):
        st.caption("ความต้องการ 3 อันดับแรกระดับประเทศ (แถว 'ทั่วประเทศ' ของ สสช.)")
        nat_df = main_df[main_df["region"] == "ทั่วประเทศ"][["year", "Need", "Iss_Need", "Iss_Need_Grouped", "Per_vill"]].copy()
        nat_df.columns = ["ปี", "อันดับ", "ปัญหาเดิม", "กลุ่ม 9 ปัญหา", "ร้อยละ (%)"]
        st.dataframe(nat_df.sort_values(by=["ปี", "อันดับ"]), hide_index=True, use_container_width=True)
        st.info("แถว 'ทั่วประเทศ' แยกออกจากการคำนวณระดับจังหวัดเพื่อป้องกันการนับซ้ำ")

# 6. ส่วนหัว Dashboard (Halloween Dark Gothic Style)
header_banner_html = (
    "<div class='dashboard-header-halloween'>"
    "<div class='header-badge-halloween'>🎃 THAILAND HALLOWEEN ISSUES RADAR 2566–2567</div>"
    "<h1>การวิเคราะห์ความต้องการให้รัฐบาลช่วยเหลือของหมู่บ้าน/ชุมชนไทย</h1>"
    "<p>"
    "วิเคราะห์ความต้องการ 3 อันดับแรกของหมู่บ้าน/ชุมชน 77 จังหวัด จำแนก 9 กลุ่มปัญหามาตรฐาน "
    "และพิสูจน์บริบทเชิงพื้นที่ด้วยข้อมูลเสริมจริง (ค่าใช้จ่ายครัวเรือน อัตราการว่างงาน และผลผลิตข้าว) "
    "โดยไม่มี Mock Data หรือคะแนนสมมติใด ๆ"
    "</p>"
    "</div>"
)
st.markdown(header_banner_html, unsafe_allow_html=True)

# 7. แถบแสดงสถานะตัวกรองปัจจุบัน (Active Filter Chips)
chip_year = f"📅 ปี {st.session_state['filter_year']}"
chip_regs = f"🏰 {len(st.session_state['filter_regions'])} ภาค" if st.session_state['filter_regions'] else "ทุกภูมิภาค"
chip_provs = f"📍 {len(st.session_state['filter_provinces'])} จังหวัด" if st.session_state['filter_provinces'] else "ทุกจังหวัด (77 จ.)"
chip_groups = f"🏷️ {len(st.session_state['filter_groups'])} กลุ่มปัญหา" if st.session_state['filter_groups'] else "9 กลุ่มปัญหา"
chip_rank = f"🏆 {st.session_state['filter_rank']}"

chips_bar_html = (
    f"<div style='margin-bottom:18px;'>"
    f"<span style='font-size:0.86rem; color:#C084FC; font-weight:600; margin-right:8px;'>ตัวกรองที่ใช้งาน:</span>"
    f"<span class='filter-chip-halloween'>{chip_year}</span>"
    f"<span class='filter-chip-halloween'>{chip_regs}</span>"
    f"<span class='filter-chip-halloween'>{chip_provs}</span>"
    f"<span class='filter-chip-halloween'>{chip_groups}</span>"
    f"<span class='filter-chip-halloween'>{chip_rank}</span>"
    f"</div>"
)
st.markdown(chips_bar_html, unsafe_allow_html=True)

# 8. โครงสร้าง 3 แท็บหลัก
tab1, tab2, tab3 = st.tabs([
    "🎃 TAB 1: ภาพรวมความเดือดร้อนระดับประเทศ",
    "👻 TAB 2: เจาะลึกรายจังหวัด & Reality Check",
    "🕸️ TAB 3: เปรียบเทียบแนวโน้มปี 2566 vs 2567"
])

global_filters_bundle = {
    "year": st.session_state["filter_year"],
    "regions": st.session_state["filter_regions"],
    "provinces": st.session_state["filter_provinces"],
    "groups": st.session_state["filter_groups"],
    "subproblem_search": st.session_state["filter_sub_search"],
    "rank": st.session_state["filter_rank"],
    "per_vill_range": st.session_state["filter_per_vill"]
}

with tab1:
    render_tab1(
        main_df=main_df,
        province_df=province_df,
        geojson_data=geojson_data,
        global_filters=global_filters_bundle
    )

with tab2:
    render_tab2(
        main_df=main_df,
        province_df=province_df,
        geojson_data=geojson_data,
        global_filters=global_filters_bundle
    )

with tab3:
    render_tab3(
        main_df=main_df,
        province_df=province_df,
        geojson_data=geojson_data,
        global_filters=global_filters_bundle
    )

# 9. ส่วนท้ายของหน้า (Footer & Methodology Notes)
st.divider()
with st.expander("📖 ระเบียบวิธีวิจัย แหล่งข้อมูลทางการ และข้อควรระวังทางสถิติ (BRD v2.0 & HANDOFF v2.0)"):
    st.markdown(
        """
        ### ระเบียบวิธีและข้อควรระวังในการแปลผล
        1. **นิยามของค่า Per_vill:** ค่า `Per_vill` คือร้อยละของหมู่บ้าน/ชุมชนในจังหวัดนั้นที่รายงานความต้องการรายการดังกล่าวใน 3 อันดับแรก ห้ามนำร้อยละของปัญหาต่างประเภทมารวมกันเป็นสัดส่วน 100% เพราะแต่ละหมู่บ้านสามารถรายงานได้หลายประเด็น และห้ามใช้คำว่า 'ร้อยละประชาชน' แทนค่านี้
        2. **สถานะการรายงานปัญหา:** การระบุว่า 'รายงานปัญหาใน 3 อันดับ' หมายถึงการติด 3 อันดับแรกของการสำรวจเท่านั้น จังหวัดที่ไม่อยู่ใน 3 อันดับมิได้หมายความว่าไม่มีปัญหานั้นอยู่จริงในพื้นที่
        3. **การวิเคราะห์เชิงพรรณนา (Descriptive Analysis):** ข้อมูลในแดชบอร์ดนี้มุ่งสะท้อนสถานการณ์และความสัมพันธ์เชิงพรรณนา ไม่สามารถอนุมานความเป็นเหตุและผล (Causal Inference) ได้
        4. **ความครอบคลุมของตัวชี้วัดเสริม:**
           - *ค่าใช้จ่ายครัวเรือนเฉลี่ยต่อเดือน:* มีข้อมูลเฉพาะปี 2567 (77 จังหวัด)
           - *ผลผลิตข้าวนาปีต่อเนื้อที่เก็บเกี่ยว:* มีข้อมูลเฉพาะปี 2567 (77 จังหวัด)
           - *อัตราการว่างงาน:* มีข้อมูลครบทั้งปี 2566 และ 2567 (77 จังหวัด)
        5. **กรณีอันดับความต้องการเสมอ (Tie Ranks):** ในปี 2567 จังหวัดระนองและหนองบัวลำภูมีรายงาน 4 รายการเนื่องจากคะแนนเสมอในอันดับที่ 1 และ 3 ตามลำดับ แดชบอร์ดคงข้อมูลไว้ครบถ้วน
        6. **แหล่งข้อมูลทางการ:**
           - ข้อมูลความต้องการของหมู่บ้าน/ชุมชน: [สำนักงานสถิติแห่งชาติ (data.go.th)](https://data.go.th/dataset/0602_00_0002)
           - ค่าใช้จ่ายครัวเรือน: [สำนักงานสถิติแห่งชาติ (data.go.th)](https://data.go.th/dataset/os_08_00009)
           - อัตราการว่างงาน: สำนักงานสภาพัฒนาการเศรษฐกิจและสังคมแห่งชาติ (สศช.) ดัชนีความก้าวหน้าของคน (HAI Databook 2567 ตารางที่ 9) สำรวจโดย สสช.
           - ผลผลิตข้าวนาปี: [สำนักงานเศรษฐกิจการเกษตร (catalog.oae.go.th)](https://catalog.oae.go.th/th/dataset/dataoae1104)
           - ขอบเขตแผนที่ 77 จังหวัด: [OpenGISData-Thailand](https://github.com/chingchai/OpenGISData-Thailand)
        """
    )
