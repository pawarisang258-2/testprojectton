"""
tab2_economy.py
แท็บ 2: เศรษฐกิจและการเงิน
วิเคราะห์ความต้องการด้านเศรษฐกิจร่วมกับค่าใช้จ่ายครัวเรือนรายจังหวัด (ปี 2567)
"""

import pandas as pd
import streamlit as st
from src.components import (
    render_kpi,
    render_source_footer,
    render_empty_state,
    create_choropleth_map,
    create_box_plot,
    create_grouped_bar
)
from src.theme import STATUS_COLORS, YEAR_COLORS


def render_tab2(main_df, province_df, geojson_data, global_year, global_provinces):
    """
    เรนเดอร์เนื้อหาและกราฟของ Tab 2: เศรษฐกิจและการเงิน
    """
    st.markdown("### 💰 เศรษฐกิจและการเงิน: ความต้องการกับค่าใช้จ่ายครัวเรือน")
    st.markdown(
        "สำรวจความต้องการด้านเศรษฐกิจและการเงิน (เช่น ค่าครองชีพ หนี้สิน แหล่งเงินทุน) "
        "เปรียบเทียบระหว่างปี 2566–2567 และวิเคราะห์ร่วมกับ **ค่าใช้จ่ายครัวเรือนเฉลี่ยต่อเดือน (ปี 2567)**"
    )

    # ตัวกรองเฉพาะแท็บ
    with st.expander("🔍 ตัวกรองเพิ่มเติมสำหรับแท็บเศรษฐกิจ", expanded=True):
        col_f1, col_f2 = st.columns(2)
        
        # ปัญหาย่อยเศรษฐกิจ
        econ_subs = sorted(
            main_df[(main_df["problem_group"] == "เศรษฐกิจและการเงิน") & (main_df["region"] != "ทั่วประเทศ")]["standard_problem"]
            .dropna().unique().tolist()
        )
        selected_sub = col_f1.selectbox("เลือกปัญหาย่อยด้านเศรษฐกิจ:", ["ทั้งหมด"] + econ_subs, index=0, key="t2_sub")

        # สถานะการรายงานปัญหา
        selected_status = col_f2.selectbox(
            "สถานะการรายงานปัญหาเศรษฐกิจ:",
            ["ทั้งหมด", "รายงานปัญหาใน 3 อันดับ", "ไม่อยู่ใน 3 อันดับ"],
            index=0,
            key="t2_status"
        )

    # เตรียมข้อมูล province_df สำหรับการคำนวณตัวชี้วัดรายจังหวัด
    prov_filtered = province_df.copy()
    if global_provinces:
        prov_filtered = prov_filtered[prov_filtered["region"].isin(global_provinces)]

    # ข้อมูลปี 2567 สำหรับค่าใช้จ่ายครัวเรือน
    prov_67 = prov_filtered[prov_filtered["year"] == 2567].copy()
    prov_66 = prov_filtered[prov_filtered["year"] == 2566].copy()

    # กรองตามสถานะการรายงานหากเลือก
    if selected_status == "รายงานปัญหาใน 3 อันดับ":
        prov_67_eval = prov_67[prov_67["has_economic_problem"] == 1]
    elif selected_status == "ไม่อยู่ใน 3 อันดับ":
        prov_67_eval = prov_67[prov_67["has_economic_problem"] == 0]
    else:
        prov_67_eval = prov_67

    # คำนวณ KPI
    reported_66 = prov_66["has_economic_problem"].sum()
    reported_67 = prov_67["has_economic_problem"].sum()
    total_eval_67 = len(prov_67)

    # ค่าใช้จ่ายเฉลี่ยปี 2567
    exp_rep = prov_67[prov_67["has_economic_problem"] == 1]["monthly_expenditure"].mean()
    exp_not_rep = prov_67[prov_67["has_economic_problem"] == 0]["monthly_expenditure"].mean()
    n_rep = (prov_67["has_economic_problem"] == 1).sum()
    n_not_rep = (prov_67["has_economic_problem"] == 0).sum()

    # แสดง KPI Cards
    st.markdown(
        f"""
        <div class='kpi-container'>
            {render_kpi("จังหวัดรายงานปัญหาปี 2567", f"{reported_67:,} <span style='font-size:1rem;'>จังหวัด</span>", f"คิดเป็น {reported_67/total_eval_67*100:.1f}% ของจังหวัดที่เลือก", "navy")}
            {render_kpi("จังหวัดรายงานปัญหาปี 2566", f"{reported_66:,} <span style='font-size:1rem;'>จังหวัด</span>", f"เปรียบเทียบปี 2566", "blue")}
            {render_kpi("ค่าใช้จ่ายเฉลี่ย (กลุ่มรายงาน)", f"{exp_rep:,.2f} <span style='font-size:1rem;'>บาท/เดือน</span>" if pd.notna(exp_rep) else "ไม่มีข้อมูล", f"n = {n_rep} จังหวัด (ปี 2567 ไม่ถ่วงน้ำหนัก)", "emerald")}
            {render_kpi("ค่าใช้จ่ายเฉลี่ย (ไม่อยู่ใน 3 อันดับ)", f"{exp_not_rep:,.2f} <span style='font-size:1rem;'>บาท/เดือน</span>" if pd.notna(exp_not_rep) else "ไม่มีข้อมูล", f"n = {n_not_rep} จังหวัด (ปี 2567 ไม่ถ่วงน้ำหนัก)", "amber")}
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. แถวเปรียบเทียบปี 2566 vs 2567 ของปัญหาเศรษฐกิจ
    st.markdown("#### ⚖️ การเปลี่ยนแปลงความต้องการด้านเศรษฐกิจระหว่างปี 2566 และ 2567")
    col_bar, col_sub_bar = st.columns([1, 1])

    with col_bar:
        # กราฟแท่งเปรียบเทียบจำนวนจังหวัดรายงานปัญหา 2566 vs 2567
        comp_summary = pd.DataFrame({
            "ปี พ.ศ.": ["2566", "2567"],
            "จำนวนจังหวัดที่รายงาน": [reported_66, reported_67]
        })
        fig_comp = create_grouped_bar(
            comp_summary,
            x_col="ปี พ.ศ.",
            y_col="จำนวนจังหวัดที่รายงาน",
            color_col="ปี พ.ศ.",
            title="จำนวนจังหวัดที่รายงานปัญหาเศรษฐกิจใน 3 อันดับแรก (2566 vs 2567)",
            subtitle="นับจังหวัดที่มีธง has_economic_problem=1 (ปี 2566 = 74 จังหวัด, ปี 2567 = 63 จังหวัด)",
            x_label="ปี พ.ศ.",
            y_label="จำนวนจังหวัด (จังหวัด)",
            color_discrete_map={"2566": YEAR_COLORS[2566], "2567": YEAR_COLORS[2567]}
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        render_source_footer(["main"])

    with col_sub_bar:
        # เปรียบเทียบปัญหาย่อยด้านเศรษฐกิจข้ามปี
        sub_comp = main_df[
            (main_df["region"] != "ทั่วประเทศ") &
            (main_df["problem_group"] == "เศรษฐกิจและการเงิน")
        ]
        if global_provinces:
            sub_comp = sub_comp[sub_comp["region"].isin(global_provinces)]
        
        sub_grouped = (
            sub_comp.groupby(["standard_problem", "year"])["region"]
            .nunique()
            .reset_index(name="prov_count")
        )
        sub_grouped["year_str"] = sub_grouped["year"].astype(str)

        fig_sub = create_grouped_bar(
            sub_grouped,
            x_col="standard_problem",
            y_col="prov_count",
            color_col="year_str",
            title="จำนวนจังหวัดที่รายงานปัญหาย่อยด้านเศรษฐกิจ (2566 vs 2567)",
            subtitle="นับจำนวนจังหวัดที่ไม่ซ้ำตามปัญหาย่อย (หมายเหตุ: ปี 2567 เพิ่มหนี้สินฯ แทนแหล่งเงินทุนฯ)",
            x_label="ปัญหาย่อยด้านเศรษฐกิจ",
            y_label="จำนวนจังหวัด (จังหวัด)",
            color_discrete_map={"2566": YEAR_COLORS[2566], "2567": YEAR_COLORS[2567]}
        )
        st.plotly_chart(fig_sub, use_container_width=True)
        render_source_footer(["main"])

    # 2. ส่วนวิเคราะห์ค่าใช้จ่ายครัวเรือน (ปี 2567 เท่านั้น)
    st.markdown("#### 🗺️ แผนที่และการกระจายตัวของค่าใช้จ่ายครัวเรือนเฉลี่ยรายจังหวัด (ปี 2567)")
    
    # แจ้งเตือนหากผู้ใช้เลือกปี 2566 ใน Global Context
    if global_year == "2566":
        render_empty_state(
            "ไม่มีข้อมูลค่าใช้จ่ายครัวเรือนสำหรับปี 2566",
            "ข้อมูลค่าใช้จ่ายครัวเรือนเฉลี่ยต่อเดือนสำรวจเฉพาะปี 2567 จึงไม่นำมาจับคู่กับข้อมูลความต้องการปี 2566"
        )
    else:
        col_map, col_box = st.columns([1.1, 1])

        with col_map:
            # แผนที่ค่าใช้จ่ายครัวเรือน ปี 2567
            map_data = prov_67_eval.copy()
            map_data["สถานะ"] = map_data["has_economic_problem"].apply(
                lambda x: "รายงานปัญหาเศรษฐกิจ" if x == 1 else "ไม่อยู่ใน 3 อันดับ"
            )
            fig_map = create_choropleth_map(
                map_data,
                geojson=geojson_data,
                location_col="region",
                color_col="monthly_expenditure",
                title="ค่าใช้จ่ายครัวเรือนเฉลี่ยต่อเดือนรายจังหวัด (ปี 2567)",
                subtitle="หน่วย: บาท/เดือน (สำรวจภาวะเศรษฐกิจและสังคมของครัวเรือน สสช.)",
                color_scale="Blues",
                hover_name="region",
                hover_data={"monthly_expenditure": ":,.2f", "สถานะ": True},
                labels={"monthly_expenditure": "ค่าใช้จ่าย (บาท/เดือน)", "สถานะ": "สถานะรายงานปัญหา"}
            )
            st.plotly_chart(fig_map, use_container_width=True)
            render_source_footer(["expenditure", "map"])

        with col_box:
            # Box Plot ค่าใช้จ่ายครัวเรือนแยกตามสถานะการรายงานปัญหา
            box_data = prov_67.copy()
            box_data["สถานะการรายงาน"] = box_data["has_economic_problem"].apply(
                lambda x: "รายงานปัญหาใน 3 อันดับ" if x == 1 else "ไม่อยู่ใน 3 อันดับ"
            )
            fig_box = create_box_plot(
                box_data,
                x_col="สถานะการรายงาน",
                y_col="monthly_expenditure",
                title="การกระจายตัวของค่าใช้จ่ายครัวเรือน ปี 2567 แยกตามสถานะรายงานปัญหา",
                subtitle="Box Plot พร้อมจุดข้อมูลจริงของทุกจังหวัด (One point per province)",
                x_label="สถานะการรายงานปัญหาเศรษฐกิจ",
                y_label="ค่าใช้จ่ายครัวเรือนเฉลี่ย (บาท/เดือน)",
                color_col="สถานะการรายงาน",
                color_discrete_map=STATUS_COLORS
            )
            st.plotly_chart(fig_box, use_container_width=True)
            render_source_footer(["expenditure"])

        # 3. Bar Chart เปรียบเทียบค่าเฉลี่ยสองกลุ่ม
        mean_df = pd.DataFrame({
            "กลุ่มสถานะ": [f"รายงานปัญหาใน 3 อันดับ\n(n={n_rep})", f"ไม่อยู่ใน 3 อันดับ\n(n={n_not_rep})"],
            "ค่าใช้จ่ายเฉลี่ย (บาท/เดือน)": [round(exp_rep, 2) if pd.notna(exp_rep) else 0,
                                           round(exp_not_rep, 2) if pd.notna(exp_not_rep) else 0],
            "สถานะ": ["รายงานปัญหาใน 3 อันดับ", "ไม่อยู่ใน 3 อันดับ"]
        })
        fig_mean = create_grouped_bar(
            mean_df,
            x_col="กลุ่มสถานะ",
            y_col="ค่าใช้จ่ายเฉลี่ย (บาท/เดือน)",
            color_col="สถานะ",
            title="ค่าใช้จ่ายครัวเรือนเฉลี่ยเปรียบเทียบระหว่างกลุ่มจังหวัด (ปี 2567)",
            subtitle="ค่าเฉลี่ยเลขคณิตของค่ารายจังหวัด (ไม่ถ่วงน้ำหนักตามจำนวนประชากร)",
            x_label="กลุ่มจังหวัดตามสถานะการรายงานปัญหา",
            y_label="ค่าใช้จ่ายเฉลี่ย (บาท/เดือน)",
            color_discrete_map=STATUS_COLORS
        )
        st.plotly_chart(fig_mean, use_container_width=True)
        render_source_footer(["expenditure"])

    # 4. ตารางเจาะลึกรายละเอียด
    st.markdown("#### 📄 ตารางรายละเอียดความต้องการด้านเศรษฐกิจและค่าใช้จ่ายครัวเรือน")
    
    # รวมข้อมูล Main Data กับตัวชี้วัดค่าใช้จ่ายรายจังหวัด
    econ_main = main_df[
        (main_df["region"] != "ทั่วประเทศ") &
        (main_df["problem_group"] == "เศรษฐกิจและการเงิน")
    ].copy()
    
    if global_year != "ทั้งสองปี":
        econ_main = econ_main[econ_main["year"] == int(global_year)]
    if global_provinces:
        econ_main = econ_main[econ_main["region"].isin(global_provinces)]
    if selected_sub != "ทั้งหมด":
        econ_main = econ_main[econ_main["standard_problem"] == selected_sub]

    # Join กับค่าใช้จ่ายปี 2567
    exp_mapping = province_df[province_df["year"] == 2567].set_index("region")["monthly_expenditure"].to_dict()
    econ_main["monthly_expenditure_2567"] = econ_main["region"].map(exp_mapping)

    display_econ = econ_main[[
        "year", "region", "Need", "standard_problem", "Iss_Need", "Per_vill", "monthly_expenditure_2567"
    ]].copy()
    display_econ.columns = [
        "ปี พ.ศ.", "จังหวัด", "อันดับ", "ปัญหาย่อย", "ข้อความระบุปัญหา", "ร้อยละหมู่บ้าน (%)", "ค่าใช้จ่ายปี 2567 (บาท/เดือน)"
    ]
    st.dataframe(
        display_econ.sort_values(by=["ปี พ.ศ.", "จังหวัด", "อันดับ"]),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"แสดงข้อมูลทั้งหมด {len(display_econ):,} รายการ")
