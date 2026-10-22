"""
tab1_overview.py
แท็บ 1: ภาพรวมความต้องการให้รัฐบาลช่วยเหลือของหมู่บ้าน/ชุมชนไทย ปี 2566–2567
"""

import pandas as pd
import streamlit as st
from src.components import (
    render_kpi,
    render_source_footer,
    render_empty_state,
    create_choropleth_map,
    create_treemap,
    create_horizontal_bar,
    create_grouped_bar
)
from src.theme import GROUP_COLORS, STATUS_COLORS, YEAR_COLORS


def render_tab1(main_df, province_df, geojson_data, global_year, global_provinces):
    """
    เรนเดอร์เนื้อหาและกราฟของ Tab 1
    """
    st.markdown("### 📋 ภาพรวมความต้องการให้รัฐบาลช่วยเหลือ (ภาพรวมประเทศและรายจังหวัด)")
    st.markdown(
        "วิเคราะห์ว่าปัญหาใดปรากฏใน **3 อันดับแรก** ของหมู่บ้าน/ชุมชนมากที่สุด มีการกระจายตัวในจังหวัดใดบ้าง "
        "และเปรียบเทียบความแตกต่างระหว่างปี 2566 และ 2567"
    )

    # 1. ตัวกรองเฉพาะแท็บ (Tab-local Filters)
    with st.expander("🔍 ตัวกรองเพิ่มเติมสำหรับแท็บภาพรวม", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        
        # กรองกลุ่มปัญหา
        all_groups = ["ทั้งหมด"] + sorted(main_df["problem_group"].dropna().unique().tolist())
        selected_group = col_f1.selectbox("เลือกกลุ่มปัญหา:", all_groups, index=0, key="t1_group")
        
        # กรองปัญหาย่อย (สัมพันธ์กับกลุ่มปัญหา)
        sub_df = main_df[main_df["region"] != "ทั่วประเทศ"]
        if selected_group != "ทั้งหมด":
            sub_df = sub_df[sub_df["problem_group"] == selected_group]
        available_subs = ["ทั้งหมด"] + sorted(sub_df["standard_problem"].dropna().unique().tolist())
        selected_sub = col_f2.selectbox("เลือกปัญหาย่อย (Standard Problem):", available_subs, index=0, key="t1_sub")

        # กรองอันดับความต้องการ
        ranks = ["ทั้งหมด", "ความต้องการ อันดับ 1", "ความต้องการ อันดับ 2", "ความต้องการ อันดับ 3"]
        selected_rank = col_f3.selectbox("เลือกอันดับความต้องการ:", ranks, index=0, key="t1_rank")

    # กรองข้อมูล Main DataFrame (ไม่รวมแถว 'ทั่วประเทศ' สำหรับการคำนวณรายจังหวัด)
    df_prov = main_df[main_df["region"] != "ทั่วประเทศ"].copy()

    # กรองตาม Global Context (ปี และ จังหวัด)
    if global_year != "ทั้งสองปี":
        df_prov = df_prov[df_prov["year"] == int(global_year)]
    
    if global_provinces:
        df_prov = df_prov[df_prov["region"].isin(global_provinces)]

    # กรองตาม Local Filters
    if selected_group != "ทั้งหมด":
        df_prov = df_prov[df_prov["problem_group"] == selected_group]
    if selected_sub != "ทั้งหมด":
        df_prov = df_prov[df_prov["standard_problem"] == selected_sub]
    if selected_rank != "ทั้งหมด":
        df_prov = df_prov[df_prov["Need"] == selected_rank]

    # คำนวณค่าทางสถิติสำหรับ KPI
    total_provinces = df_prov["region"].nunique()
    total_groups = df_prov["problem_group"].nunique()
    total_records = len(df_prov)

    # ปัญหาที่พบบ่อยสุดในชุดข้อมูลที่กรอง
    top_group_name = "-"
    top_group_count = 0
    if not df_prov.empty:
        top_group_series = df_prov.groupby("problem_group")["region"].nunique().sort_values(ascending=False)
        if not top_group_series.empty:
            top_group_name = top_group_series.index[0]
            top_group_count = top_group_series.iloc[0]

    # แสดง KPI Cards
    st.markdown(
        f"""
        <div class='kpi-container'>
            {render_kpi("จังหวัดที่ผ่านเงื่อนไข", f"{total_provinces:,} <span style='font-size:1rem;'>จังหวัด</span>", "จากทั้งหมด 77 จังหวัด", "navy")}
            {render_kpi("กลุ่มปัญหาที่พบ", f"{total_groups:,} <span style='font-size:1rem;'>กลุ่ม</span>", "จากทั้งหมด 6 กลุ่มมาตรฐาน", "blue")}
            {render_kpi("จำนวนรายการความต้องการ", f"{total_records:,} <span style='font-size:1rem;'>รายการ</span>", "รวมรายการอันดับเสมอ", "emerald")}
            {render_kpi("กลุ่มปัญหาที่พบมากสุด", f"{top_group_name}", f"พบใน {top_group_count} จังหวัด", "amber")}
        </div>
        """,
        unsafe_allow_html=True
    )

    if df_prov.empty:
        render_empty_state("ไม่พบข้อมูลตามเงื่อนไขตัวกรองที่เลือก", "กรุณาปรับตัวกรองปี จังหวัด หรือกลุ่มปัญหาใหม่")
        return

    # 2. แถวแสดง Treemap และ Horizontal Bar Chart
    col_left, col_right = st.columns([1, 1])

    with col_left:
        # Treemap แสดงจำนวนจังหวัดต่อกลุ่มปัญหา
        # คำนวณจำนวนจังหวัดที่ไม่ซ้ำต่อกลุ่ม
        treemap_data = (
            df_prov.groupby(["problem_group"])["region"]
            .nunique()
            .reset_index(name="prov_count")
        )
        treemap_fig = create_treemap(
            treemap_data,
            path_cols=["problem_group"],
            values_col="prov_count",
            title=f"การกระจายตัวของกลุ่มปัญหา (ปี {global_year})",
            subtitle="จำนวนจังหวัดที่รายงาน (หนึ่งจังหวัดรายงานได้หลายกลุ่ม จึงไม่ใช่สัดส่วนรวม 100%)",
            color_col="problem_group",
            color_discrete_map=GROUP_COLORS
        )
        st.plotly_chart(treemap_fig, use_container_width=True)
        render_source_footer(["main"])

    with col_right:
        # Horizontal Bar Chart อันดับกลุ่มปัญหา
        ranking_data = (
            df_prov.groupby("problem_group")["region"]
            .nunique()
            .reset_index(name="prov_count")
        )
        ranking_fig = create_horizontal_bar(
            ranking_data,
            x_col="prov_count",
            y_col="problem_group",
            title=f"อันดับกลุ่มปัญหาที่ปรากฏใน 3 อันดับแรก (ปี {global_year})",
            subtitle="นับจำนวนจังหวัดที่ไม่ซ้ำที่รายงานแต่ละกลุ่มปัญหา (หน่วย: จังหวัด)",
            x_label="จำนวนจังหวัดที่รายงาน",
            y_label="กลุ่มปัญหา",
            color_col="problem_group",
            color_discrete_map=GROUP_COLORS
        )
        st.plotly_chart(ranking_fig, use_container_width=True)
        render_source_footer(["main"])

    # 3. แผนที่ Choropleth แสดงการกระจายตัวระดับจังหวัด
    st.markdown("#### 🗺️ แผนที่การกระจายตัวของปัญหาเชิงพื้นที่")
    
    # เตรียมข้อมูลสำหรับแผนที่
    # ดึงรายชื่อ 77 จังหวัดทั้งหมดเพื่อไม่ให้แผนที่แหว่ง
    all_77_provinces = sorted(province_df["region"].unique())
    map_year = 2567 if global_year in ["2567", "ทั้งสองปี"] else 2566

    map_base = pd.DataFrame({"region": all_77_provinces})
    
    # ตรวจสอบว่าเลือกปัญหาย่อยหรือไม่
    if selected_sub != "ทั้งหมด":
        # กรณีเลือกปัญหาย่อย: แสดง Per_vill จริงของปัญหาย่อยนั้น
        sub_prov_map = df_prov[df_prov["standard_problem"] == selected_sub][["region", "Per_vill", "Need"]].drop_duplicates("region")
        map_df = pd.merge(map_base, sub_prov_map, on="region", how="left")
        map_df["สถานะ"] = map_df["Per_vill"].apply(lambda v: f"รายงาน ({v:.1f}%)" if pd.notna(v) else "ไม่อยู่ใน 3 อันดับ")
        
        map_fig = create_choropleth_map(
            map_df,
            geojson=geojson_data,
            location_col="region",
            color_col="Per_vill",
            title=f"ร้อยละหมู่บ้าน/ชุมชนที่ต้องการความช่วยเหลือ: {selected_sub} (ปี {global_year})",
            subtitle=f"แสดงค่า Per_vill (%) ของปัญหาย่อย '{selected_sub}' ในแต่ละจังหวัด (พื้นที่สีเทา = ไม่อยู่ใน 3 อันดับ)",
            color_scale="Blues",
            hover_name="region",
            hover_data={"Per_vill": ":.1f", "Need": True, "สถานะ": True},
            labels={"Per_vill": "ร้อยละหมู่บ้าน (%)", "Need": "อันดับความต้องการ", "สถานะ": "สถานะการรายงาน"}
        )
    else:
        # กรณีเลือกกลุ่มปัญหา หรือดูภาพรวม: แสดงสถานะว่ารายงานกลุ่มนั้นหรือไม่
        reported_provs = set(df_prov["region"].unique())
        map_df = map_base.copy()
        map_df["สถานะการรายงาน"] = map_df["region"].apply(
            lambda r: "รายงานปัญหาใน 3 อันดับ" if r in reported_provs else "ไม่อยู่ใน 3 อันดับ"
        )
        
        map_fig = create_choropleth_map(
            map_df,
            geojson=geojson_data,
            location_col="region",
            color_col="สถานะการรายงาน",
            title=f"จังหวัดที่รายงานความต้องการ: {selected_group} (ปี {global_year})",
            subtitle="จำแนกจังหวัดที่รายงานปัญหาใน 3 อันดับแรกเทียบกับจังหวัดที่ไม่ได้รายงาน",
            is_discrete=True,
            color_discrete_map=STATUS_COLORS,
            hover_name="region",
            hover_data={"สถานะการรายงาน": True},
            labels={"สถานะการรายงาน": "สถานะ"}
        )

    st.plotly_chart(map_fig, use_container_width=True)
    render_source_footer(["main", "map"])

    # 4. กราฟเปรียบเทียบปี 2566 vs 2567 (Grouped Bar Chart)
    st.markdown("#### ⚖️ การเปรียบเทียบความต้องการระหว่างปี 2566 และ 2567")
    
    # คำนวณเปรียบเทียบรายกลุ่ม 2 ปี โดยกรองตามจังหวัดและกลุ่มที่เลือก
    comp_df_all = main_df[main_df["region"] != "ทั่วประเทศ"].copy()
    if global_provinces:
        comp_df_all = comp_df_all[comp_df_all["region"].isin(global_provinces)]
    if selected_group != "ทั้งหมด":
        comp_df_all = comp_df_all[comp_df_all["problem_group"] == selected_group]

    comp_grouped = (
        comp_df_all.groupby(["problem_group", "year"])["region"]
        .nunique()
        .reset_index(name="prov_count")
    )
    comp_grouped["year_str"] = comp_grouped["year"].astype(str)

    comp_fig = create_grouped_bar(
        comp_grouped,
        x_col="problem_group",
        y_col="prov_count",
        color_col="year_str",
        title="เปรียบเทียบจำนวนจังหวัดที่รายงานแต่ละกลุ่มปัญหา: ปี 2566 เทียบ ปี 2567",
        subtitle="จำนวนจังหวัดที่ไม่ซ้ำที่รายงานแต่ละกลุ่มปัญหาใน 3 อันดับแรก (เปรียบเทียบเคียงข้างกัน)",
        x_label="กลุ่มปัญหา",
        y_label="จำนวนจังหวัดที่รายงาน (จังหวัด)",
        color_discrete_map={"2566": YEAR_COLORS[2566], "2567": YEAR_COLORS[2567]}
    )
    st.plotly_chart(comp_fig, use_container_width=True)
    render_source_footer(["main"])

    # 5. ตารางเจาะลึกข้อมูล 3 อันดับแรก (Detail Table)
    st.markdown("#### 📄 ตารางข้อมูลความต้องการเจาะลึกรายจังหวัด")
    display_cols = [
        "year", "region", "Need", "Iss_Need", "standard_problem", "problem_group", "Per_vill"
    ]
    table_df = df_prov[display_cols].copy()
    table_df.columns = [
        "ปี พ.ศ.", "จังหวัด", "อันดับความต้องการ", "ข้อความปัญหาต้นฉบับ",
        "ปัญหามาตรฐาน (Standard)", "กลุ่มปัญหา", "ร้อยละหมู่บ้าน/ชุมชน (%)"
    ]
    st.dataframe(
        table_df.sort_values(by=["ปี พ.ศ.", "จังหวัด", "อันดับความต้องการ"]),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"แสดงข้อมูลทั้งหมด {len(table_df):,} รายการ (รวมกรณีอันดับเสมอ เช่น ระนอง และ หนองบัวลำภู ปี 2567)")
