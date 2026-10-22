"""
app.py
แอปพลิเคชันหลัก Interactive Dashboard:
การวิเคราะห์ความต้องการให้รัฐบาลช่วยเหลือของหมู่บ้าน/ชุมชนไทย ปี 2566–2567
พัฒนาด้วย Python, Streamlit, Pandas และ Plotly
"""

import streamlit as st
import pandas as pd
from src.data_loader import load_all_data, get_provinces_list
from src.theme import CUSTOM_CSS
from src.tab1_overview import render_tab1
from src.tab2_economy import render_tab2
from src.tab3_employment import render_tab3
from src.tab4_agriculture import render_tab4

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(
    page_title="ความต้องการให้รัฐบาลช่วยเหลือของหมู่บ้าน/ชุมชนไทย ปี 2566–2567",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. นำเข้า CSS ปรับแต่งความสวยงาม
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. โหลดข้อมูลจริง (Cached)
try:
    main_df, province_df, comparison_df, geojson_data = load_all_data()
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
    st.stop()

# 4. ฟังก์ชันจัดการ State ของตัวกรองส่วนกลาง (Global Filter State)
if "global_year" not in st.session_state:
    st.session_state["global_year"] = "2567"

if "selected_provinces" not in st.session_state:
    st.session_state["selected_provinces"] = []


def reset_all_filters():
    """รีเซ็ตตัวกรองทั้งหมดกลับสู่ค่าเริ่มต้น"""
    st.session_state["global_year"] = "2567"
    st.session_state["selected_provinces"] = []
    
    # รีเซ็ตตัวกรองในแต่ละแท็บ
    tab_keys = [
        "t1_group", "t1_sub", "t1_rank",
        "t2_sub", "t2_status",
        "t3_sub", "t3_status", "t3_top_n", "t3_sort_mode",
        "t4_sub", "t4_status"
    ]
    for k in tab_keys:
        if k in st.session_state:
            del st.session_state[k]


# 5. แถบควบคุมด้านข้าง (Sidebar Controls)
with st.sidebar:
    st.markdown("### ⚙️ ตัวกรองข้อมูลส่วนกลาง")
    st.caption("การปรับค่าที่นี่จะส่งผลต่อการวิเคราะห์ในทุกแท็บ")

    # ตัวเลือกปี
    st.session_state["global_year"] = st.radio(
        "เลือกปีการสำรวจ:",
        ["2567", "2566", "ทั้งสองปี"],
        index=["2567", "2566", "ทั้งสองปี"].index(st.session_state["global_year"]),
        help="ปี 2567 เป็นข้อมูลล่าสุด; หากเลือกทั้งสองปีจะแสดงผลเปรียบเทียบในกราฟที่รองรับ"
    )

    # ตัวเลือกจังหวัด
    all_provinces = get_provinces_list(province_df)
    
    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("เลือกทุกจังหวัด", use_container_width=True):
        st.session_state["selected_provinces"] = []
        st.rerun()
    if col_btn2.button("ล้างตัวกรอง", type="secondary", use_container_width=True):
        reset_all_filters()
        st.rerun()

    st.session_state["selected_provinces"] = st.multiselect(
        "เลือกจังหวัดที่ต้องการวิเคราะห์:",
        options=all_provinces,
        default=st.session_state["selected_provinces"],
        placeholder="ทุกจังหวัด (77 จังหวัด)",
        help="เว้นว่างไว้เพื่อดูข้อมูลครบทั้ง 77 จังหวัด หรือเลือกเฉพาะจังหวัดที่สนใจ"
    )

    st.divider()

    # ข้อมูลบริบทภาพรวมประเทศ (National Benchmark)
    with st.expander("📌 ข้อมูล 3 อันดับแรกภาพรวมประเทศ", expanded=False):
        st.caption("ความต้องการ 3 อันดับแรกในระดับภาพรวมประเทศ (จากแถว 'ทั่วประเทศ' ของ สสช.)")
        nat_df = main_df[main_df["region"] == "ทั่วประเทศ"][["year", "Need", "standard_problem", "Per_vill"]].copy()
        nat_df.columns = ["ปี", "อันดับ", "ปัญหา", "ร้อยละหมู่บ้าน (%)"]
        st.dataframe(nat_df.sort_values(by=["ปี", "อันดับ"]), hide_index=True, use_container_width=True)
        st.info("หมายเหตุ: แถวทั่วประเทศถูกแยกออกจากการคำนวณระดับจังหวัดเพื่อป้องกันการนับซ้ำ")

    st.divider()
    st.markdown(
        """
        <div style='font-size:0.8rem; color:#64748B; line-height:1.5;'>
            <b>จัดทำเพื่อการวิเคราะห์ทางวิชาการ</b><br>
            โดยใช้ภาษา Python, Streamlit, Pandas และ Plotly<br>
            ข้อมูลจริง 100% ตามข้อกำหนด BRD และ HANDOFF
        </div>
        """,
        unsafe_allow_html=True
    )

# 6. Header ส่วนหัวของ Dashboard
st.markdown(
    """
    <div class='dashboard-header'>
        <div class='header-badge'>Interactive Analytics Dashboard</div>
        <h1>การวิเคราะห์ความต้องการให้รัฐบาลช่วยเหลือของหมู่บ้าน/ชุมชนไทย</h1>
        <p>
            การสำรวจความต้องการ 3 อันดับแรกของหมู่บ้าน/ชุมชนระดับจังหวัด ประจำปี พ.ศ. 2566 และ 2567 
            ร่วมกับบริบทค่าใช้จ่ายครัวเรือน อัตราการว่างงาน และผลผลิตข้าวนาปี
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 7. แถบแสดงสถานะตัวกรองที่กำลังใช้งาน (Active Filter Chips)
active_year = st.session_state["global_year"]
active_provs = st.session_state["selected_provinces"]
prov_chip_text = f"{len(active_provs)} จังหวัดที่เลือก" if active_provs else "ทุกจังหวัด (77 จังหวัด)"

chips_html = f"""
<div style='margin-bottom: 14px;'>
    <span style='font-size:0.85rem; color:#475569; font-weight:600; margin-right:8px;'>ตัวกรองปัจจุบัน:</span>
    <span class='filter-chip'>📅 ปี พ.ศ. {active_year}</span>
    <span class='filter-chip'>📍 {prov_chip_text}</span>
</div>
"""
st.markdown(chips_html, unsafe_allow_html=True)

# 8. โครงสร้างแท็บหลักทั้ง 4 แท็บ
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Tab 1: ภาพรวมความต้องการ",
    "💰 Tab 2: เศรษฐกิจและการเงิน",
    "💼 Tab 3: อาชีพและการจ้างงาน",
    "🌾 Tab 4: เกษตรกรรมและที่ดิน"
])

with tab1:
    render_tab1(
        main_df=main_df,
        province_df=province_df,
        geojson_data=geojson_data,
        global_year=active_year,
        global_provinces=active_provs
    )

with tab2:
    render_tab2(
        main_df=main_df,
        province_df=province_df,
        geojson_data=geojson_data,
        global_year=active_year,
        global_provinces=active_provs
    )

with tab3:
    render_tab3(
        main_df=main_df,
        province_df=province_df,
        geojson_data=geojson_data,
        global_year=active_year,
        global_provinces=active_provs
    )

with tab4:
    render_tab4(
        main_df=main_df,
        province_df=province_df,
        geojson_data=geojson_data,
        global_year=active_year,
        global_provinces=active_provs
    )

# 9. ส่วนท้ายของหน้า (Footer & Methodology Notes)
st.divider()
with st.expander("📖 คำอธิบายระเบียบวิธี ขอบเขตข้อมูล และข้อจำกัดทางสถิติ (Data Limitations & Methodology)"):
    st.markdown(
        """
        ### ระเบียบวิธีและข้อควรระวังในการแปลผล
        1. **นิยามของตัวชี้วัด Per_vill:** ค่า `Per_vill` คือร้อยละของหมู่บ้าน/ชุมชนในจังหวัดนั้นที่รายงานความต้องการรายการดังกล่าวใน 3 อันดับแรก ห้ามนำร้อยละของปัญหาต่างประเภทมารวมกันเป็นสัดส่วน 100% เพราะแต่ละหมู่บ้านสามารถรายงานได้หลายประเด็น
        2. **สถานะการรายงานปัญหา:** การระบุว่า 'รายงานปัญหา' หรือ 'ไม่อยู่ใน 3 อันดับ' หมายถึงการปรากฏใน 3 อันดับแรกของการสำรวจเท่านั้น จังหวัดที่ไม่อยู่ใน 3 อันดับมิได้หมายความว่าไม่มีปัญหานั้นอยู่จริงในพื้นที่
        3. **การวิเคราะห์เชิงพรรณนา (Descriptive Analysis):** ข้อมูลในแดชบอร์ดนี้มุ่งสะท้อนสถานการณ์และความสัมพันธ์เชิงพรรณนา ไม่สามารถอนุมานความเป็นเหตุและผล (Causal Inference) ได้
        4. **ความครอบคลุมของตัวชี้วัดเสริม:**
           - *ค่าใช้จ่ายครัวเรือนเฉลี่ยต่อเดือน:* มีข้อมูลเฉพาะปี 2567 (77 จังหวัด)
           - *ผลผลิตข้าวนาปีต่อเนื้อที่เก็บเกี่ยว:* มีข้อมูลเฉพาะปี 2567 (77 จังหวัด)
           - *อัตราการว่างงาน:* มีข้อมูลครบทั้งปี 2566 และ 2567 (77 จังหวัด)
        5. **กรณีอันดับความต้องการเสมอ (Tie Ranks):** ในปี 2567 จังหวัดระนองและหนองบัวลำภูมีรายงาน 4 รายการเนื่องจากคะแนนเสมอในอันดับที่ 1 และ 3 ตามลำดับ แดชบอร์ดคงข้อมูลไว้ครบทั้ง 4 รายการตามต้นฉบับ
        6. **แหล่งข้อมูลทางการ:**
           - ข้อมูลความต้องการของหมู่บ้าน/ชุมชน: [สำนักงานสถิติแห่งชาติ (data.go.th)](https://data.go.th/dataset/0602_00_0002)
           - ค่าใช้จ่ายครัวเรือน: [สำนักงานสถิติแห่งชาติ (data.go.th)](https://data.go.th/dataset/os_08_00009)
           - อัตราการว่างงาน: สำนักงานสภาพัฒนาการเศรษฐกิจและสังคมแห่งชาติ (สศช.) HAI Databook 2567 ตารางที่ 9 (สำรวจโดย สสช.)
           - ผลผลิตข้าวนาปี: [สำนักงานเศรษฐกิจการเกษตร (catalog.oae.go.th)](https://catalog.oae.go.th/th/dataset/dataoae1104)
           - ขอบเขตแผนที่ 77 จังหวัด: [OpenGISData-Thailand](https://github.com/chingchai/OpenGISData-Thailand)
        """
    )
