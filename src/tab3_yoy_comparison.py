"""
tab3_yoy_comparison.py
แท็บ 3: เปรียบเทียบแนวโน้มปี 2566 vs 2567 (YoY Trend) — Halloween Edition
Multi-Line YoY Trend Chart, Overall Issue Slope Chart, Rising & Falling และ Rank 1 Shift
(ลบกราฟแนวโน้มอัตราการว่างงานออกตามข้อกำหนด)
"""

import pandas as pd
import streamlit as st
from src.components import (
    render_kpi_halloween,
    render_source_footer,
    render_empty_state_halloween,
    create_multi_line_yoy_halloween,
    create_slope_chart_halloween,
    create_grouped_bar_halloween
)
from src.theme import (
    GROUP_COLORS_9,
    YEAR_COLORS_HALLOWEEN
)


def render_tab3(main_df, province_df, geojson_data, global_filters):
    """
    เรนเดอร์เนื้อหา Tab 3: เปรียบเทียบแนวโน้มปี 2566 vs 2567 ตามแม่แบบ halloween_dashboard.html
    """
    st.markdown("### 🕸️ การเปรียบเทียบแนวโน้มความต้องการปี 2566 เทียบ ปี 2567 (YoY Trend)")
    st.markdown(
        "ติดตามการเปลี่ยนแปลงความถี่ของ 9 กลุ่มปัญหา ระบุกลุ่มปัญหาที่มีการพุ่งสูงขึ้น (Spike) หรือลดลง "
        "และสำรวจการสับเปลี่ยนอันดับ 1 ของแต่ละจังหวัด ระหว่างปี พ.ศ. 2566 และ 2567"
    )

    # 1. แถบตัวกรองเฉพาะแท็บ (Dual Filter Bar: ภูมิภาค & หมวดหมู่ปัญหา)
    with st.expander("🔍 ตัวกรองเพิ่มเติมสำหรับแท็บเปรียบเทียบ (YoY Filters)", expanded=True):
        col_f1, col_f2 = st.columns(2)
        
        all_regions = ["🌐 ทั่วประเทศ (ทุกภาค)"] + sorted(
            main_df[main_df["region"] != "ทั่วประเทศ"]["region_group"].dropna().unique().tolist()
        )
        selected_reg = col_f1.selectbox("ภูมิภาค:", all_regions, index=0, key="t3_line_reg")

        all_groups = ["🎃 ทุกหมวดหมู่ปัญหา (9 ด้าน)"] + sorted(
            main_df["Iss_Need_Grouped"].dropna().unique().tolist()
        )
        selected_group = col_f2.selectbox("หมวดหมู่ปัญหา:", all_groups, index=0, key="t3_line_group")

    # กรองข้อมูล
    df_scope = main_df[main_df["region"] != "ทั่วประเทศ"].copy()
    if selected_reg != "🌐 ทั่วประเทศ (ทุกภาค)":
        df_scope = df_scope[df_scope["region_group"] == selected_reg]
    if global_filters["provinces"]:
        df_scope = df_scope[df_scope["region"].isin(global_filters["provinces"])]

    # 2. คำนวณจำนวนจังหวัดที่รายงานแต่ละกลุ่ม 9 กลุ่ม ในแต่ละปี
    counts_by_year_group = (
        df_scope.groupby(["Iss_Need_Grouped", "year"])["region"]
        .nunique()
        .reset_index(name="prov_count")
    )

    # Pivot เพื่อหาผลต่าง (Delta)
    piv = counts_by_year_group.pivot(index="Iss_Need_Grouped", columns="year", values="prov_count").fillna(0)
    if 2566 not in piv.columns:
        piv[2566] = 0
    if 2567 not in piv.columns:
        piv[2567] = 0
    piv["diff_provinces"] = piv[2567] - piv[2566]
    piv = piv.reset_index()

    # หายอดรวมกลุ่มที่เพิ่มขึ้นและลดลง
    top_rising = piv.sort_values(by="diff_provinces", ascending=False).iloc[0] if not piv.empty else None
    top_falling = piv.sort_values(by="diff_provinces", ascending=True).iloc[0] if not piv.empty else None

    if top_rising is not None:
        r_name = str(top_rising["Iss_Need_Grouped"])
        r_diff = int(top_rising["diff_provinces"])
        r_66 = int(top_rising[2566])
        r_67 = int(top_rising[2567])
        r_sub = f"เพิ่มขึ้น {r_diff:+d} จังหวัด ({r_66} ➔ {r_67} จ.)"
    else:
        r_name = "-"
        r_sub = ""

    if top_falling is not None:
        f_name = str(top_falling["Iss_Need_Grouped"])
        f_diff = int(top_falling["diff_provinces"])
        f_66 = int(top_falling[2566])
        f_67 = int(top_falling[2567])
        f_sub = f"ลดลง {f_diff:+d} จังหวัด ({f_66} ➔ {f_67} จ.)"
    else:
        f_name = "-"
        f_sub = ""

    # แสดง KPI Cards (ไม่มี 4-space indentation)
    kpi_tab3_html = (
        f"<div class='kpi-container'>"
        f"{render_kpi_halloween('กลุ่มปัญหาที่เพิ่มขึ้นสูงสุด (Spike)', r_name, r_sub, 'blood')}"
        f"{render_kpi_halloween('กลุ่มปัญหาที่ลดลงมากสุด', f_name, f_sub, 'green')}"
        f"{render_kpi_halloween('กลุ่มปัญหาที่ติดตาม', '9 กลุ่มมาตรฐาน', 'ครอบคลุมทุกมิติสังคม-เศรษฐกิจ', 'purple')}"
        f"{render_kpi_halloween('ช่วงปีเปรียบเทียบ', '2566 vs 2567', 'สำรวจ 77 จังหวัด (154 จังหวัด-ปี)', 'orange')}"
        f"</div>"
    )
    st.markdown(kpi_tab3_html, unsafe_allow_html=True)

    # 3. SECTION 1: Interactive Multi-Line YoY Trend Chart
    st.markdown("#### 📈 SECTION 1: Interactive Multi-Line YoY Trend Chart (กราฟเส้นเปรียบเทียบแนวโน้ม 2566 vs 2567)")
    
    line_data = counts_by_year_group.copy()
    if selected_group != "🎃 ทุกหมวดหมู่ปัญหา (9 ด้าน)":
        line_data = line_data[line_data["Iss_Need_Grouped"] == selected_group]

    line_data["year_str"] = line_data["year"].astype(str)

    fig_lines = create_multi_line_yoy_halloween(
        line_data,
        x_col="year_str",
        y_col="prov_count",
        color_col="Iss_Need_Grouped",
        title=f"แนวโน้มจำนวนจังหวัดที่รายงานปัญหา (ปี 2566 vs 2567) — {selected_reg}",
        subtitle="เปรียบเทียบจำนวนจังหวัดที่ไม่ซ้ำที่รายงานแต่ละกลุ่มปัญหาใน 3 อันดับแรก"
    )
    st.plotly_chart(fig_lines, use_container_width=True)
    render_source_footer(["main"])

    # 4. SECTION 2: Overall Issue Slope / Trend Chart
    st.markdown("#### 📉 SECTION 2: Overall Issue Slope / Trend Chart (ทิศทางความเปลี่ยนแปลงข้ามปี)")
    st.markdown(
        "<div style='font-size:0.85rem; color:#CBD5E1; margin-bottom:8px;'>"
        "เส้นสีแดง (<b style='color:#FF0055;'>Spike</b>) = กลุ่มปัญหาที่พบเพิ่มขึ้น | เส้นสีเขียว/เทา = กลุ่มปัญหาที่ลดลงหรือทรงตัว"
        "</div>",
        unsafe_allow_html=True
    )

    slope_piv = piv.copy()
    if selected_group != "🎃 ทุกหมวดหมู่ปัญหา (9 ด้าน)":
        slope_piv = slope_piv[slope_piv["Iss_Need_Grouped"] == selected_group]

    fig_slope = create_slope_chart_halloween(
        slope_piv,
        title="Slope Chart แสดงทิศทางการเพิ่มขึ้น/ลดลงของ 9 กลุ่มปัญหา",
        subtitle=f"ผลต่างจำนวนจังหวัดระหว่างปี 2566 และ 2567 (พื้นที่: {selected_reg})"
    )
    st.plotly_chart(fig_slope, use_container_width=True)
    render_source_footer(["main"])

    # 5. SECTION 3: สรุปกลุ่มปัญหา Rising & Falling
    st.markdown("#### 📊 ตารางสรุปการเปลี่ยนแปลง (Rising & Falling Groups)")
    
    piv_table = piv.copy()
    piv_table["ทิศทาง"] = piv_table["diff_provinces"].apply(
        lambda d: "🔺 เพิ่มขึ้น (Spike)" if d > 0 else ("🔻 ลดลง" if d < 0 else "➖ คงเดิม")
    )
    piv_table = piv_table[["Iss_Need_Grouped", 2566, 2567, "diff_provinces", "ทิศทาง"]].rename(
        columns={
            "Iss_Need_Grouped": "กลุ่มปัญหา 9 กลุ่ม",
            2566: "จำนวนจังหวัด ปี 2566",
            2567: "จำนวนจังหวัด ปี 2567",
            "diff_provinces": "ผลต่าง (จังหวัด)"
        }
    ).sort_values(by="ผลต่าง (จังหวัด)", ascending=False)

    st.dataframe(piv_table, hide_index=True, use_container_width=True)

    # 6. SECTION 4: การสับเปลี่ยนอันดับ 1 (Rank 1 Transition Matrix)
    st.markdown("#### 🔄 การเปลี่ยนแปลงกลุ่มปัญหา 'อันดับ 1' รายจังหวัด (Rank 1 Shift)")
    
    rank1_df = df_scope[df_scope["Need"] == "ความต้องการ อันดับ 1"].copy()
    r1_piv = rank1_df.pivot_table(
        index="region",
        columns="year",
        values="Iss_Need_Grouped",
        aggfunc=lambda x: ", ".join(sorted(set(x)))
    ).dropna()

    if 2566 in r1_piv.columns and 2567 in r1_piv.columns:
        r1_piv["สถานะการเปลี่ยนแปลง"] = r1_piv.apply(
            lambda row: "เปลี่ยนกลุ่มปัญหาอันดับ 1" if row[2566] != row[2567] else "คงเดิม (กลุ่มเดิม)",
            axis=1
        )
        r1_piv = r1_piv.reset_index()
        reg_map = main_df.drop_duplicates("region").set_index("region")["region_group"].to_dict()
        r1_piv["region_group"] = r1_piv["region"].map(reg_map)

        n_changed = (r1_piv["สถานะการเปลี่ยนแปลง"] == "เปลี่ยนกลุ่มปัญหาอันดับ 1").sum()
        n_same = (r1_piv["สถานะการเปลี่ยนแปลง"] == "คงเดิม (กลุ่มเดิม)").sum()

        col_st1, col_st2 = st.columns([1, 1.5])
        with col_st1:
            stat_box_html = (
                f"<div style='background:rgba(20,20,35,0.85); border:1px solid rgba(138,43,226,0.35); border-radius:12px; padding:16px; margin-bottom:12px;'>"
                f"<div style='color:#FF9E4A; font-weight:700; margin-bottom:6px;'>สถิติการสับเปลี่ยนอันดับ 1</div>"
                f"<div style='font-size:1.35rem; font-weight:700; color:#FFFFFF;'>{n_changed} <span style='font-size:0.9rem; font-weight:normal; color:#CBD5E1;'>จังหวัดเปลี่ยนอันดับ 1 ({n_changed/len(r1_piv)*100:.1f}%)</span></div>"
                f"<div style='font-size:1.1rem; font-weight:600; color:#00FF66; margin-top:4px;'>{n_same} <span style='font-size:0.9rem; font-weight:normal; color:#CBD5E1;'>จังหวัดคงอันดับ 1 เดิม ({n_same/len(r1_piv)*100:.1f}%)</span></div>"
                f"</div>"
            )
            st.markdown(stat_box_html, unsafe_allow_html=True)

        with col_st2:
            shift_filter = st.radio(
                "กรองสถานะการสับเปลี่ยน:",
                ["ทั้งหมด", "เปลี่ยนกลุ่มปัญหาอันดับ 1", "คงเดิม (กลุ่มเดิม)"],
                index=0,
                horizontal=True,
                key="t3_shift_radio"
            )

        r1_display = r1_piv.copy()
        if shift_filter != "ทั้งหมด":
            r1_display = r1_display[r1_display["สถานะการเปลี่ยนแปลง"] == shift_filter]

        r1_display = r1_display[["region_group", "region", 2566, 2567, "สถานะการเปลี่ยนแปลง"]].rename(
            columns={
                "region_group": "ภูมิภาค",
                "region": "จังหวัด",
                2566: "กลุ่มปัญหาอันดับ 1 (ปี 2566)",
                2567: "กลุ่มปัญหาอันดับ 1 (ปี 2567)"
            }
        )
        st.dataframe(
            r1_display.sort_values(by=["ภูมิภาค", "จังหวัด"]),
            hide_index=True,
            use_container_width=True
        )

    # 7. ข้อสังเกตเชิงสถิติ (Statistical Note)
    st.markdown(
        "<div style='font-size:0.83rem; color:#CBD5E1; line-height:1.5; background:rgba(20,20,35,0.7); padding:12px 14px; border-radius:10px; border-left:3px solid #8A2BE2; margin-top:14px;'>"
        "⚠️ <b>หมายเหตุระเบียบวิธี:</b> ชุดข้อมูลนี้ครอบคลุมการสำรวจ 2 ปี (พ.ศ. 2566 และ 2567) "
        "การเปรียบเทียบในหน้านี้จึงสะท้อนความแตกต่างเชิงประจักษ์ระหว่าง 2 จุดเวลา "
        "มิใช่การพยากรณ์แนวโน้มระยะยาว (Time-series Forecasting) หรือการพิสูจน์สาเหตุและผลลัพธ์"
        "</div>",
        unsafe_allow_html=True
    )
    render_source_footer(["main"])
