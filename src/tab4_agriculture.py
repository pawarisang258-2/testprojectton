"""
tab4_agriculture.py
แท็บ 4: เกษตรกรรมและที่ดิน
วิเคราะห์ความต้องการด้านเกษตรกรรมร่วมกับผลผลิตข้าวนาปีต่อไร่รายจังหวัด (ปี 2567)
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


def render_tab4(main_df, province_df, geojson_data, global_year, global_provinces):
    """
    เรนเดอร์เนื้อหาและกราฟของ Tab 4: เกษตรกรรมและที่ดิน
    """
    st.markdown("### 🌾 เกษตรกรรมและที่ดิน: ความต้องการกับผลผลิตข้าวนาปี")
    st.markdown(
        "สำรวจความต้องการด้านการเกษตรและที่ดินทำกิน เปรียบเทียบระหว่างปี 2566–2567 "
        "และวิเคราะห์ร่วมกับ **ผลผลิตข้าวนาปีต่อเนื้อที่เก็บเกี่ยวรายจังหวัด (กก./ไร่)** ซึ่งมีข้อมูลสำรวจในปี 2567"
    )

    # ตัวกรองเฉพาะแท็บ
    with st.expander("🔍 ตัวกรองเพิ่มเติมสำหรับแท็บเกษตรกรรม", expanded=True):
        col_f1, col_f2 = st.columns(2)
        
        agri_subs = sorted(
            main_df[(main_df["problem_group"] == "เกษตรกรรมและที่ดิน") & (main_df["region"] != "ทั่วประเทศ")]["standard_problem"]
            .dropna().unique().tolist()
        )
        selected_sub = col_f1.selectbox("เลือกปัญหาย่อยด้านเกษตรกรรม:", ["ทั้งหมด"] + agri_subs, index=0, key="t4_sub")

        selected_status = col_f2.selectbox(
            "สถานะการรายงานปัญหาเกษตรกรรม:",
            ["ทั้งหมด", "รายงานปัญหาใน 3 อันดับ", "ไม่อยู่ใน 3 อันดับ"],
            index=0,
            key="t4_status"
        )

    # เตรียมข้อมูล province_df สำหรับการคำนวณตัวชี้วัดรายจังหวัด
    prov_filtered = province_df.copy()
    if global_provinces:
        prov_filtered = prov_filtered[prov_filtered["region"].isin(global_provinces)]

    prov_67 = prov_filtered[prov_filtered["year"] == 2567].copy()
    prov_66 = prov_filtered[prov_filtered["year"] == 2566].copy()

    # จำนวนจังหวัดรายงานปัญหา
    reported_66 = prov_66["has_agriculture_problem"].sum()
    reported_67 = prov_67["has_agriculture_problem"].sum()
    total_eval_67 = len(prov_67)

    # ผลผลิตข้าวเฉลี่ยปี 2567
    rice_rep = prov_67[prov_67["has_agriculture_problem"] == 1]["rice_yield_per_rai"].mean()
    rice_not_rep = prov_67[prov_67["has_agriculture_problem"] == 0]["rice_yield_per_rai"].mean()
    n_rep = (prov_67["has_agriculture_problem"] == 1).sum()
    n_not_rep = (prov_67["has_agriculture_problem"] == 0).sum()

    # แสดง KPI Cards
    st.markdown(
        f"""
        <div class='kpi-container'>
            {render_kpi("จังหวัดรายงานปัญหาปี 2567", f"{reported_67:,} <span style='font-size:1rem;'>จังหวัด</span>", f"คิดเป็น {reported_67/total_eval_67*100:.1f}% ของจังหวัดที่เลือก", "navy")}
            {render_kpi("จังหวัดรายงานปัญหาปี 2566", f"{reported_66:,} <span style='font-size:1rem;'>จังหวัด</span>", f"ปี 2566 รายงาน {reported_66} จังหวัด", "blue")}
            {render_kpi("ผลผลิตข้าวเฉลี่ย (กลุ่มรายงาน)", f"{rice_rep:,.2f} <span style='font-size:1rem;'>กก./ไร่</span>" if pd.notna(rice_rep) else "ไม่มีข้อมูล", f"n = {n_rep} จังหวัด (ปี 2567 ไม่ถ่วงน้ำหนัก)", "emerald")}
            {render_kpi("ผลผลิตข้าวเฉลี่ย (ไม่อยู่ใน 3 อันดับ)", f"{rice_not_rep:,.2f} <span style='font-size:1rem;'>กก./ไร่</span>" if pd.notna(rice_not_rep) else "ไม่มีข้อมูล", f"n = {n_not_rep} จังหวัด (ปี 2567 ไม่ถ่วงน้ำหนัก)", "amber")}
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. แถวเปรียบเทียบปี 2566 vs 2567
    st.markdown("#### ⚖️ การเปรียบเทียบความต้องการด้านเกษตรกรรมระหว่างปี 2566 และ 2567")
    col_bar, col_sub_bar = st.columns([1, 1])

    with col_bar:
        # เปรียบเทียบจำนวนจังหวัดรายงานปัญหา 2566 vs 2567
        agri_summary = pd.DataFrame({
            "ปี พ.ศ.": ["2566", "2567"],
            "จำนวนจังหวัดที่รายงาน": [reported_66, reported_67]
        })
        fig_agri_bar = create_grouped_bar(
            agri_summary,
            x_col="ปี พ.ศ.",
            y_col="จำนวนจังหวัดที่รายงาน",
            color_col="ปี พ.ศ.",
            title="จำนวนจังหวัดที่รายงานปัญหาเกษตรกรรมใน 3 อันดับแรก (2566 vs 2567)",
            subtitle="นับจังหวัดที่มีธง has_agriculture_problem=1 (ทั้งสองปีมีจำนวน 69 จังหวัดเท่ากัน)",
            x_label="ปี พ.ศ.",
            y_label="จำนวนจังหวัด (จังหวัด)",
            color_discrete_map={"2566": YEAR_COLORS[2566], "2567": YEAR_COLORS[2567]}
        )
        st.plotly_chart(fig_agri_bar, use_container_width=True)
        render_source_footer(["main"])

    with col_sub_bar:
        # แสดงปัญหาย่อยด้านเกษตรกรรม
        agri_comp = main_df[
            (main_df["region"] != "ทั่วประเทศ") &
            (main_df["problem_group"] == "เกษตรกรรมและที่ดิน")
        ]
        if global_provinces:
            agri_comp = agri_comp[agri_comp["region"].isin(global_provinces)]

        agri_sub_grouped = (
            agri_comp.groupby(["standard_problem", "year"])["region"]
            .nunique()
            .reset_index(name="prov_count")
        )
        agri_sub_grouped["year_str"] = agri_sub_grouped["year"].astype(str)

        fig_agri_sub = create_grouped_bar(
            agri_sub_grouped,
            x_col="standard_problem",
            y_col="prov_count",
            color_col="year_str",
            title="จำนวนจังหวัดที่รายงานปัญหาย่อยด้านเกษตรกรรม (2566 vs 2567)",
            subtitle="ข้อควรระวัง: ปี 2567 ปัญหาปุ๋ย น้ำ และราคา ถูกจัดรวมเป็น 'ปัญหาการเกษตรหลายด้าน'",
            x_label="ปัญหาย่อยด้านเกษตรกรรม",
            y_label="จำนวนจังหวัด (จังหวัด)",
            color_discrete_map={"2566": YEAR_COLORS[2566], "2567": YEAR_COLORS[2567]}
        )
        st.plotly_chart(fig_agri_sub, use_container_width=True)
        render_source_footer(["main"])

    # 2. ส่วนวิเคราะห์ผลผลิตข้าวนาปีต่อไร่ (ปี 2567 เท่านั้น)
    st.markdown("#### 🗺️ แผนที่และการกระจายตัวของผลผลิตข้าวนาปีต่อเนื้อที่เก็บเกี่ยว (ปี 2567)")

    if global_year == "2566":
        render_empty_state(
            "ไม่มีข้อมูลผลผลิตข้าวนาปีสำหรับปี 2566",
            "ข้อมูลผลผลิตข้าวนาปีต่อไร่ในชุดข้อมูลเสริมมีเฉพาะปี 2567 จึงไม่นำมาจับคู่กับปัญหาปี 2566"
        )
    else:
        col_map, col_box = st.columns([1.1, 1])

        with col_map:
            # แผนที่ผลผลิตข้าวนาปี
            map_data = prov_67.copy()
            if selected_status == "รายงานปัญหาใน 3 อันดับ":
                map_data = map_data[map_data["has_agriculture_problem"] == 1]
            elif selected_status == "ไม่อยู่ใน 3 อันดับ":
                map_data = map_data[map_data["has_agriculture_problem"] == 0]

            map_data["สถานะ"] = map_data["has_agriculture_problem"].apply(
                lambda x: "รายงานปัญหาเกษตร" if x == 1 else "ไม่อยู่ใน 3 อันดับ"
            )
            fig_map = create_choropleth_map(
                map_data,
                geojson=geojson_data,
                location_col="region",
                color_col="rice_yield_per_rai",
                title="ผลผลิตข้าวนาปีต่อเนื้อที่เก็บเกี่ยวรายจังหวัด (ปี 2567)",
                subtitle="หน่วย: กิโลกรัมต่อไร่ (สถิติการปลูกข้าวนาปี สำนักงานเศรษฐกิจการเกษตร)",
                color_scale="Greens",
                hover_name="region",
                hover_data={"rice_yield_per_rai": ":,.2f", "สถานะ": True},
                labels={"rice_yield_per_rai": "ผลผลิต (กก./ไร่)", "สถานะ": "สถานะรายงานปัญหา"}
            )
            st.plotly_chart(fig_map, use_container_width=True)
            render_source_footer(["rice", "map"])

        with col_box:
            # Box Plot ผลผลิตข้าวนาปีแยกตามสถานะ
            box_data = prov_67.copy()
            box_data["สถานะการรายงาน"] = box_data["has_agriculture_problem"].apply(
                lambda x: "รายงานปัญหาใน 3 อันดับ" if x == 1 else "ไม่อยู่ใน 3 อันดับ"
            )
            fig_box = create_box_plot(
                box_data,
                x_col="สถานะการรายงาน",
                y_col="rice_yield_per_rai",
                title="การกระจายตัวของผลผลิตข้าวนาปี ปี 2567 แยกตามสถานะรายงานปัญหา",
                subtitle="Box Plot พร้อมจุดข้อมูลจริงของทุกจังหวัด (One point per province)",
                x_label="สถานะการรายงานปัญหาเกษตรกรรม",
                y_label="ผลผลิตข้าวนาปี (กก./ไร่)",
                color_col="สถานะการรายงาน",
                color_discrete_map=STATUS_COLORS
            )
            st.plotly_chart(fig_box, use_container_width=True)
            render_source_footer(["rice"])

        # 3. Bar Chart เปรียบเทียบค่าเฉลี่ย
        mean_rice_df = pd.DataFrame({
            "กลุ่มสถานะ": [f"รายงานปัญหาใน 3 อันดับ\n(n={n_rep})", f"ไม่อยู่ใน 3 อันดับ\n(n={n_not_rep})"],
            "ผลผลิตข้าวเฉลี่ย (กก./ไร่)": [round(rice_rep, 2) if pd.notna(rice_rep) else 0,
                                            round(rice_not_rep, 2) if pd.notna(rice_not_rep) else 0],
            "สถานะ": ["รายงานปัญหาใน 3 อันดับ", "ไม่อยู่ใน 3 อันดับ"]
        })
        fig_mean_rice = create_grouped_bar(
            mean_rice_df,
            x_col="กลุ่มสถานะ",
            y_col="ผลผลิตข้าวเฉลี่ย (กก./ไร่)",
            color_col="สถานะ",
            title="ผลผลิตข้าวนาปีเฉลี่ยต่อไร่เปรียบเทียบระหว่างกลุ่มจังหวัด (ปี 2567)",
            subtitle="ค่าเฉลี่ยเลขคณิตของค่ารายจังหวัด (ไม่ถ่วงน้ำหนักตามพื้นที่เพาะปลูก)",
            x_label="กลุ่มจังหวัดตามสถานะการรายงานปัญหา",
            y_label="ผลผลิตข้าวเฉลี่ย (กก./ไร่)",
            color_discrete_map=STATUS_COLORS
        )
        st.plotly_chart(fig_mean_rice, use_container_width=True)
        render_source_footer(["rice"])

    # 4. ตารางเจาะลึกรายละเอียด
    st.markdown("#### 📄 ตารางรายละเอียดความต้องการด้านเกษตรกรรมและผลผลิตข้าวนาปี")
    
    agri_main = main_df[
        (main_df["region"] != "ทั่วประเทศ") &
        (main_df["problem_group"] == "เกษตรกรรมและที่ดิน")
    ].copy()

    if global_year != "ทั้งสองปี":
        agri_main = agri_main[agri_main["year"] == int(global_year)]
    if global_provinces:
        agri_main = agri_main[agri_main["region"].isin(global_provinces)]
    if selected_sub != "ทั้งหมด":
        agri_main = agri_main[agri_main["standard_problem"] == selected_sub]

    # Join กับผลผลิตข้าวปี 2567
    rice_mapping = province_df[province_df["year"] == 2567].set_index("region")["rice_yield_per_rai"].to_dict()
    agri_main["rice_yield_2567"] = agri_main["region"].map(rice_mapping)

    display_agri = agri_main[[
        "year", "region", "Need", "standard_problem", "Iss_Need", "Per_vill", "rice_yield_2567"
    ]].copy()
    display_agri.columns = [
        "ปี พ.ศ.", "จังหวัด", "อันดับ", "ปัญหาย่อย", "ข้อความระบุปัญหา", "ร้อยละหมู่บ้าน (%)", "ผลผลิตข้าวปี 2567 (กก./ไร่)"
    ]
    st.dataframe(
        display_agri.sort_values(by=["ปี พ.ศ.", "จังหวัด", "อันดับ"]),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"แสดงข้อมูลทั้งหมด {len(display_agri):,} รายการ")
