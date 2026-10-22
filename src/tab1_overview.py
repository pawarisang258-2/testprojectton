"""
tab1_overview.py
แท็บ 1: ภาพรวมระดับประเทศ (National Overview) — Halloween Edition
ปรับแผนที่ประเทศไทยให้มีขนาดใหญ่ ขอบเขต 77 จังหวัดชัดเจน และ Treemap แสดงเฉพาะ 9 กลุ่มปัญหาหลัก
"""

import pandas as pd
import streamlit as st
from src.components import (
    render_kpi_halloween,
    render_source_footer,
    render_empty_state_halloween,
    create_donut_chart_halloween,
    create_treemap_halloween,
    create_horizontal_bar_halloween,
    create_choropleth_map_halloween
)
from src.theme import GROUP_COLORS_9, STATUS_COLORS_HALLOWEEN


def render_tab1(main_df, province_df, geojson_data, global_filters):
    """
    เรนเดอร์เนื้อหา Tab 1: ภาพรวมระดับประเทศ
    """
    st.markdown("### 🎃 ภาพรวมความต้องการให้รัฐบาลช่วยเหลือระดับประเทศ")
    st.markdown(
        "วิเคราะห์ภาพรวมรายการความต้องการ 3 อันดับแรกของหมู่บ้าน/ชุมชนไทย จำแนก 9 กลุ่มปัญหามาตรฐาน "
        "สำรวจการกระจายตัวเชิงพื้นที่ 6 ภูมิภาค 77 จังหวัด และสัดส่วนรายการความต้องการที่รายงาน"
    )

    # 1. กรองข้อมูลตาม Global Filters (ไม่รวมแถว 'ทั่วประเทศ' สำหรับการคำนวณระดับจังหวัด)
    df_filtered = main_df[main_df["region"] != "ทั่วประเทศ"].copy()

    # กรองปี
    if global_filters["year"] != "ทั้งหมด":
        df_filtered = df_filtered[df_filtered["year"] == int(global_filters["year"])]

    # กรองภูมิภาค
    if global_filters["regions"]:
        df_filtered = df_filtered[df_filtered["region_group"].isin(global_filters["regions"])]

    # กรองจังหวัด
    if global_filters["provinces"]:
        df_filtered = df_filtered[df_filtered["region"].isin(global_filters["provinces"])]

    # กรองกลุ่มปัญหา 9 กลุ่ม
    if global_filters["groups"]:
        df_filtered = df_filtered[df_filtered["Iss_Need_Grouped"].isin(global_filters["groups"])]

    # กรองปัญหาย่อย (ค้นหาคำ)
    if global_filters["subproblem_search"]:
        df_filtered = df_filtered[df_filtered["Iss_Need"].str.contains(global_filters["subproblem_search"], na=False)]

    # กรองอันดับความต้องการ
    if global_filters["rank"] != "ทั้งหมด":
        df_filtered = df_filtered[df_filtered["Need"] == global_filters["rank"]]

    # กรองช่วง Per_vill
    min_pv, max_pv = global_filters["per_vill_range"]
    df_filtered = df_filtered[(df_filtered["Per_vill"] >= min_pv) & (df_filtered["Per_vill"] <= max_pv)]

    # คำนวณ KPI ภาพรวม
    total_provs = df_filtered["region"].nunique()
    total_groups = df_filtered["Iss_Need_Grouped"].nunique()
    total_records = len(df_filtered)

    top_group_name = "-"
    top_group_count = 0
    if not df_filtered.empty:
        top_group_series = df_filtered.groupby("Iss_Need_Grouped")["region"].nunique().sort_values(ascending=False)
        if not top_group_series.empty:
            top_group_name = top_group_series.index[0]
            top_group_count = top_group_series.iloc[0]

    # แสดง KPI Cards (ไม่มี 4-space indentation)
    kpi_html = (
        f"<div class='kpi-container'>"
        f"{render_kpi_halloween('จังหวัดที่ผ่านเงื่อนไข', f'{total_provs:,} <span style=\"font-size:1rem;\">จังหวัด</span>', 'จากทั้งหมด 77 จังหวัด', 'orange')}"
        f"{render_kpi_halloween('กลุ่มปัญหาที่พบ', f'{total_groups:,} <span style=\"font-size:1rem;\">กลุ่ม</span>', 'จากทั้งหมด 9 กลุ่มมาตรฐาน', 'purple')}"
        f"{render_kpi_halloween('จำนวนรายการใน Top 3', f'{total_records:,} <span style=\"font-size:1rem;\">รายการ</span>', 'รวมกรณีอันดับเสมอตามจริง', 'green')}"
        f"{render_kpi_halloween('กลุ่มปัญหาที่พบมากสุด', f'{top_group_name}', f'พบใน {top_group_count} จังหวัด', 'blood')}"
        f"</div>"
    )
    st.markdown(kpi_html, unsafe_allow_html=True)

    if df_filtered.empty:
        render_empty_state_halloween(
            "ไม่พบข้อมูลตามเงื่อนไขตัวกรองที่เลือก",
            "กรุณาปรับตัวกรองปี ภูมิภาค จังหวัด หรือช่วงร้อยละความต้องการใหม่"
        )
        return

    # 2. แถว Donut Chart และ Horizontal Bar Chart
    col_donut, col_bar = st.columns([1, 1.2])

    with col_donut:
        # Donut Chart แสดงสัดส่วนจำนวนรายการใน Top 3
        donut_data = (
            df_filtered.groupby("Iss_Need_Grouped")
            .size()
            .reset_index(name="record_count")
            .sort_values(by="record_count", ascending=False)
        )
        fig_donut = create_donut_chart_halloween(
            donut_data,
            names_col="Iss_Need_Grouped",
            values_col="record_count",
            title="สัดส่วนจำนวนรายการความต้องการใน Top 3 (9 กลุ่มปัญหา)",
            subtitle="ฐานการคำนวณ: ร้อยละของจำนวนรายการที่บันทึก (ไม่ใช่สัดส่วนหมู่บ้านเดือดร้อน)"
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        render_source_footer(["main"])

    with col_bar:
        # Horizontal Bar Chart นับจำนวนจังหวัดไม่ซ้ำต่อกลุ่มปัญหา
        ranking_data = (
            df_filtered.groupby("Iss_Need_Grouped")["region"]
            .nunique()
            .reset_index(name="prov_count")
        )
        fig_bar = create_horizontal_bar_halloween(
            ranking_data,
            x_col="prov_count",
            y_col="Iss_Need_Grouped",
            title="อันดับกลุ่มปัญหาที่ปรากฏใน 3 อันดับแรกของจังหวัด",
            subtitle="นับจำนวนจังหวัดที่ไม่ซ้ำที่รายงานแต่ละกลุ่มปัญหา (หน่วย: จังหวัด)",
            x_label="จำนวนจังหวัดที่รายงาน (จังหวัด)",
            y_label="กลุ่มปัญหา 9 กลุ่ม"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        render_source_footer(["main"])

    # 3. Treemap แสดงเฉพาะ 9 กลุ่มปัญหาหลัก (ไม่มีการแตกปัญหาย่อยภายใน)
    st.markdown("#### 🌳 National Issues Treemap (จำแนกเฉพาะ 9 กลุ่มปัญหาหลัก)")
    
    # นับจำนวนจังหวัดไม่ซ้ำภายในแต่ละกลุ่มปัญหา
    tm_data = (
        df_filtered.groupby("Iss_Need_Grouped")["region"]
        .nunique()
        .reset_index(name="prov_count")
    )
    # คำนวณร้อยละของจังหวัดที่พบกลุ่มนั้น
    total_prov_in_scope = df_filtered["region"].nunique()
    
    fig_tm = create_treemap_halloween(
        tm_data,
        path_cols=["Iss_Need_Grouped"],
        values_col="prov_count",
        title="การกระจายตัวของ 9 กลุ่มปัญหาหลัก (ขนาดกล่องสัมพันธ์กับจำนวนจังหวัด)",
        subtitle=f"คำนวณจากจำนวนจังหวัดที่ไม่ซ้ำที่รายงานปัญหาในแต่ละกลุ่ม (ปี {global_filters['year']})",
        color_col="Iss_Need_Grouped"
    )
    st.plotly_chart(fig_tm, use_container_width=True)
    render_source_footer(["main"])

    # 4. แผนที่ประเทศไทยระดับจังหวัด (Choropleth Map 77 จังหวัดขนาดใหญ่)
    st.markdown("#### 🗺️ Authentic Thailand Heat Map (รูปทรงจริงครบ 77 จังหวัด)")

    col_map_opt1, col_map_opt2 = st.columns([1, 1])
    map_mode = col_map_opt1.selectbox(
        "เลือกมิติข้อมูลสำหรับแสดงบนแผนที่:",
        [
            "สถานะการรายงานกลุ่มปัญหาที่เลือก (มี/ไม่มีรายงานใน 3 อันดับ)",
            "จำนวนรายการปัญหาที่ติด 3 อันดับแรกในแต่ละจังหวัด (ความหนาแน่น)",
            "ร้อยละหมู่บ้าน/ชุมชน (Per_vill) ของปัญหาย่อยที่เลือก"
        ],
        index=0,
        key="t1_map_mode"
    )

    all_77 = sorted(province_df["region"].unique())
    map_base = pd.DataFrame({"region": all_77})
    reg_map = main_df.drop_duplicates("region").set_index("region")["region_group"].to_dict()
    map_base["region_group"] = map_base["region"].map(reg_map)

    # จัดการเรื่องปี: หากเลือกปี 'ทั้งหมด' แผนที่แสดงข้อมูลปีล่าสุด 2567 หรือปีที่ระบุ
    map_year_label = "2567 (ปีล่าสุด)" if global_filters["year"] == "ทั้งหมด" else f"ปี {global_filters['year']}"
    df_for_map = df_filtered.copy()
    if global_filters["year"] == "ทั้งหมด":
        df_for_map = df_for_map[df_for_map["year"] == 2567]

    if map_mode == "สถานะการรายงานกลุ่มปัญหาที่เลือก (มี/ไม่มีรายงานใน 3 อันดับ)":
        target_group = col_map_opt2.selectbox(
            "เลือกกลุ่มปัญหาที่ต้องการส่องบนแผนที่:",
            sorted(main_df["Iss_Need_Grouped"].dropna().unique()),
            index=0,
            key="t1_map_target_group"
        )
        rep_provs = set(df_for_map[df_for_map["Iss_Need_Grouped"] == target_group]["region"].unique())
        map_df = map_base.copy()
        map_df["สถานะ"] = map_df["region"].apply(
            lambda r: "รายงานปัญหาใน 3 อันดับ" if r in rep_provs else "ไม่อยู่ใน 3 อันดับ"
        )
        map_df["ปี พ.ศ."] = map_year_label
        map_df["กลุ่มปัญหา"] = target_group

        fig_map = create_choropleth_map_halloween(
            map_df,
            geojson=geojson_data,
            location_col="region",
            color_col="สถานะ",
            title=f"แผนที่จังหวัดที่รายงานปัญหา: {target_group} ({map_year_label})",
            subtitle=f"สีส้ม = รายงานใน 3 อันดับ ({len(rep_provs)} จังหวัด) | สีม่วงเข้ม = ไม่อยู่ใน 3 อันดับ ({77 - len(rep_provs)} จังหวัด)",
            is_discrete=True,
            color_discrete_map={
                "รายงานปัญหาใน 3 อันดับ": "#FF6B00",
                "ไม่อยู่ใน 3 อันดับ": "#261E38"
            },
            hover_name="region",
            hover_data={"region_group": True, "กลุ่มปัญหา": True, "ปี พ.ศ.": True, "สถานะ": True},
            labels={"region_group": "ภูมิภาค", "สถานะ": "สถานะการรายงาน"}
        )

    elif map_mode == "จำนวนรายการปัญหาที่ติด 3 อันดับแรกในแต่ละจังหวัด (ความหนาแน่น)":
        counts = df_for_map.groupby("region").size().to_dict()
        map_df = map_base.copy()
        map_df["จำนวนรายการ"] = map_df["region"].map(counts).fillna(0).astype(int)
        map_df["ปี พ.ศ."] = map_year_label
        
        fig_map = create_choropleth_map_halloween(
            map_df,
            geojson=geojson_data,
            location_col="region",
            color_col="จำนวนรายการ",
            title=f"แผนที่จำนวนรายการความต้องการใน 3 อันดับแรก ({map_year_label})",
            subtitle="สะท้อนความหนาแน่นของรายการปัญหา (สีสว่าง = รายการมาก, สีมืด = รายการน้อย/ไม่มีรายการ)",
            color_scale=[
                [0, "#1A1526"],
                [0.25, "#581C87"],
                [0.5, "#9333EA"],
                [0.75, "#EA580C"],
                [1, "#FF6B00"]
            ],
            hover_name="region",
            hover_data={"region_group": True, "ปี พ.ศ.": True, "จำนวนรายการ": True},
            labels={"region_group": "ภูมิภาค", "จำนวนรายการ": "จำนวนรายการ"}
        )

    else:
        # ร้อยละ Per_vill ของปัญหาย่อย
        available_subs = sorted(df_for_map["Iss_Need"].unique())
        if not available_subs:
            available_subs = sorted(main_df["Iss_Need"].unique())
        target_sub = col_map_opt2.selectbox(
            "เลือกปัญหาย่อยสำหรับดูค่า Per_vill (%):",
            available_subs,
            index=0,
            key="t1_map_target_sub"
        )
        sub_data = df_for_map[df_for_map["Iss_Need"] == target_sub].drop_duplicates("region")
        sub_pv_map = sub_data.set_index("region")["Per_vill"].to_dict()
        sub_need_map = sub_data.set_index("region")["Need"].to_dict()

        map_df = map_base.copy()
        map_df["Per_vill"] = map_df["region"].map(sub_pv_map)
        map_df["Need"] = map_df["region"].map(sub_need_map).fillna("ไม่อยู่ใน 3 อันดับ")
        map_df["สถานะ"] = map_df["Per_vill"].apply(lambda v: f"รายงาน ({v:.1f}%)" if pd.notna(v) else "ไม่อยู่ใน 3 อันดับ")
        map_df["ปี พ.ศ."] = map_year_label
        map_df["ปัญหาย่อย"] = target_sub

        fig_map = create_choropleth_map_halloween(
            map_df,
            geojson=geojson_data,
            location_col="region",
            color_col="Per_vill",
            title=f"ร้อยละหมู่บ้าน/ชุมชนที่ต้องการความช่วยเหลือ: {target_sub} ({map_year_label})",
            subtitle=f"แสดงค่า Per_vill (%) ของปัญหาย่อยเฉพาะ (พื้นที่สีม่วงเข้ม = ไม่อยู่ใน 3 อันดับ)",
            color_scale=[
                [0, "#261E38"],
                [0.25, "#6D28D9"],
                [0.55, "#C026D3"],
                [0.8, "#EA580C"],
                [1, "#FF6B00"]
            ],
            hover_name="region",
            hover_data={"region_group": True, "ปี พ.ศ.": True, "ปัญหาย่อย": True, "Per_vill": ":.1f", "Need": True, "สถานะ": True},
            labels={"region_group": "ภูมิภาค", "Per_vill": "ร้อยละหมู่บ้าน (%)", "Need": "อันดับ", "สถานะ": "สถานะ"}
        )

    st.plotly_chart(fig_map, use_container_width=True)
    render_source_footer(["main", "map"])

    # 5. ตารางข้อมูลเจาะลึก
    st.markdown("#### 📄 ตารางข้อมูลความต้องการที่ผ่านการกรอง")
    display_df = df_filtered[[
        "year", "region_group", "region", "Need", "Iss_Need", "Iss_Need_Grouped", "Per_vill"
    ]].copy()
    display_df.columns = [
        "ปี พ.ศ.", "ภูมิภาค", "จังหวัด", "อันดับความต้องการ", "ข้อความระบุปัญหา", "กลุ่มปัญหา 9 กลุ่ม", "ร้อยละหมู่บ้าน/ชุมชน (%)"
    ]
    st.dataframe(
        display_df.sort_values(by=["ปี พ.ศ.", "ภูมิภาค", "จังหวัด", "อันดับความต้องการ"]),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"แสดงผลรวม {len(display_df):,} รายการ จากทั้งหมด 77 จังหวัด")
