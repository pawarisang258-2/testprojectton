"""
tab3_employment.py
แท็บ 3: อาชีพและการจ้างงาน
วิเคราะห์ความต้องการด้านอาชีพร่วมกับอัตราการว่างงานรายจังหวัด ปี 2566–2567
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from src.components import (
    render_kpi,
    render_source_footer,
    render_empty_state,
    create_choropleth_map,
    create_box_plot,
    create_grouped_bar
)
from src.theme import STATUS_COLORS, YEAR_COLORS, apply_plotly_theme, FONT_FAMILY


def render_tab3(main_df, province_df, geojson_data, global_year, global_provinces):
    """
    เรนเดอร์เนื้อหาและกราฟของ Tab 3: อาชีพและการจ้างงาน
    """
    st.markdown("### 💼 อาชีพและการจ้างงาน: ความต้องการกับอัตราการว่างงาน")
    st.markdown(
        "สำรวจความต้องการด้านอาชีพ (การว่างงาน, ค่าแรง, อาชีพเสริม) "
        "และวิเคราะห์ร่วมกับ **อัตราการว่างงานรายจังหวัด (%)** ซึ่งมีข้อมูลครบถ้วนทั้งปี 2566 และ 2567"
    )

    # ตัวกรองเฉพาะแท็บ
    with st.expander("🔍 ตัวกรองเพิ่มเติมสำหรับแท็บอาชีพ", expanded=True):
        col_f1, col_f2 = st.columns(2)
        
        emp_subs = sorted(
            main_df[(main_df["problem_group"] == "อาชีพและการจ้างงาน") & (main_df["region"] != "ทั่วประเทศ")]["standard_problem"]
            .dropna().unique().tolist()
        )
        selected_sub = col_f1.selectbox("เลือกปัญหาย่อยด้านอาชีพ:", ["ทั้งหมด"] + emp_subs, index=0, key="t3_sub")

        selected_status = col_f2.selectbox(
            "สถานะการรายงานปัญหาอาชีพ:",
            ["ทั้งหมด", "รายงานปัญหาใน 3 อันดับ", "ไม่อยู่ใน 3 อันดับ"],
            index=0,
            key="t3_status"
        )

    # เตรียมข้อมูลจังหวัด
    prov_filtered = province_df.copy()
    if global_provinces:
        prov_filtered = prov_filtered[prov_filtered["region"].isin(global_provinces)]

    prov_66 = prov_filtered[prov_filtered["year"] == 2566].copy()
    prov_67 = prov_filtered[prov_filtered["year"] == 2567].copy()

    # คำนวณจำนวนจังหวัดรายงานปัญหา
    reported_66 = prov_66["has_employment_problem"].sum()
    reported_67 = prov_67["has_employment_problem"].sum()

    # อัตราว่างงานเฉลี่ย
    unemp_rep_66 = prov_66[prov_66["has_employment_problem"] == 1]["unemployment_rate"].mean()
    unemp_not_66 = prov_66[prov_66["has_employment_problem"] == 0]["unemployment_rate"].mean()
    unemp_rep_67 = prov_67[prov_67["has_employment_problem"] == 1]["unemployment_rate"].mean()
    unemp_not_67 = prov_67[prov_67["has_employment_problem"] == 0]["unemployment_rate"].mean()

    # ปีที่ใช้สำหรับแผนที่และ KPI
    eval_year = 2567 if global_year in ["2567", "ทั้งสองปี"] else 2566
    prov_eval = prov_67 if eval_year == 2567 else prov_66
    rep_eval = reported_67 if eval_year == 2567 else reported_66
    unemp_rep_eval = unemp_rep_67 if eval_year == 2567 else unemp_rep_66
    unemp_not_eval = unemp_not_67 if eval_year == 2567 else unemp_not_66

    st.markdown(
        f"""
        <div class='kpi-container'>
            {render_kpi(f"จังหวัดรายงานปัญหา (ปี {eval_year})", f"{rep_eval:,} <span style='font-size:1rem;'>จังหวัด</span>", f"ปี 2566: {reported_66} จ. | ปี 2567: {reported_67} จ.", "navy")}
            {render_kpi(f"อัตราว่างงานเฉลี่ย (กลุ่มรายงาน {eval_year})", f"{unemp_rep_eval:.2f}%", f"n = {rep_eval} จังหวัด (ไม่ถ่วงน้ำหนัก)", "amber")}
            {render_kpi(f"อัตราว่างงานเฉลี่ย (ไม่อยู่ใน 3 อันดับ)", f"{unemp_not_eval:.2f}%", f"n = {len(prov_eval)-rep_eval} จังหวัด (ไม่ถ่วงน้ำหนัก)", "blue")}
            {render_kpi("การเปลี่ยนแปลงอัตราว่างงานภาพรวม", f"{(prov_67['unemployment_rate'].mean() - prov_66['unemployment_rate'].mean()):+.2f} ppt", "ส่วนต่างระหว่างปี 2566–2567 (จุดเปอร์เซ็นต์)", "emerald")}
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. แถวเปรียบเทียบปี 2566 vs 2567
    st.markdown("#### ⚖️ การเปรียบเทียบความต้องการด้านอาชีพระหว่างปี 2566 และ 2567")
    col_bar1, col_bar2 = st.columns([1, 1])

    with col_bar1:
        # เปรียบเทียบจำนวนจังหวัดที่รายงาน
        emp_counts_df = pd.DataFrame({
            "ปี พ.ศ.": ["2566", "2567"],
            "จำนวนจังหวัดที่รายงาน": [reported_66, reported_67]
        })
        fig_emp_count = create_grouped_bar(
            emp_counts_df,
            x_col="ปี พ.ศ.",
            y_col="จำนวนจังหวัดที่รายงาน",
            color_col="ปี พ.ศ.",
            title="จำนวนจังหวัดที่รายงานปัญหาอาชีพใน 3 อันดับแรก (2566 vs 2567)",
            subtitle="นับจังหวัดที่มีธง has_employment_problem=1 (ลดลงจาก 47 เหลือ 29 จังหวัด)",
            x_label="ปี พ.ศ.",
            y_label="จำนวนจังหวัด (จังหวัด)",
            color_discrete_map={"2566": YEAR_COLORS[2566], "2567": YEAR_COLORS[2567]}
        )
        st.plotly_chart(fig_emp_count, use_container_width=True)
        render_source_footer(["main"])

    with col_bar2:
        # อัตราว่างงานเฉลี่ย 2 กลุ่ม แยกปี 2566 และ 2567
        mean_unemp_df = pd.DataFrame({
            "สถานะการรายงาน": [
                "รายงานปัญหาใน 3 อันดับ", "ไม่อยู่ใน 3 อันดับ",
                "รายงานปัญหาใน 3 อันดับ", "ไม่อยู่ใน 3 อันดับ"
            ],
            "ปี พ.ศ.": ["2566", "2566", "2567", "2567"],
            "อัตราการว่างงานเฉลี่ย (%)": [
                round(unemp_rep_66, 2), round(unemp_not_66, 2),
                round(unemp_rep_67, 2), round(unemp_not_67, 2)
            ]
        })
        fig_mean_unemp = create_grouped_bar(
            mean_unemp_df,
            x_col="สถานะการรายงาน",
            y_col="อัตราการว่างงานเฉลี่ย (%)",
            color_col="ปี พ.ศ.",
            title="อัตราการว่างงานเฉลี่ยตามสถานะการรายงาน (ปี 2566 เทียบ 2567)",
            subtitle="ค่าเฉลี่ยเลขคณิตรายจังหวัด (ไม่ถ่วงน้ำหนักตามจำนวนประชากรแรงงาน)",
            x_label="สถานะการรายงานปัญหา",
            y_label="อัตราการว่างงานเฉลี่ย (%)",
            color_discrete_map={"2566": YEAR_COLORS[2566], "2567": YEAR_COLORS[2567]}
        )
        st.plotly_chart(fig_mean_unemp, use_container_width=True)
        render_source_footer(["unemployment"])

    # 2. แผนที่และ Box Plot
    st.markdown(f"#### 🗺️ แผนที่อัตราการว่างงานและการกระจายตัวเชิงสถิติ (ปี {eval_year})")
    col_map, col_box = st.columns([1.1, 1])

    with col_map:
        # แผนที่อัตราการว่างงาน
        map_data = prov_eval.copy()
        if selected_status == "รายงานปัญหาใน 3 อันดับ":
            map_data = map_data[map_data["has_employment_problem"] == 1]
        elif selected_status == "ไม่อยู่ใน 3 อันดับ":
            map_data = map_data[map_data["has_employment_problem"] == 0]

        map_data["สถานะ"] = map_data["has_employment_problem"].apply(
            lambda x: "รายงานปัญหาอาชีพ" if x == 1 else "ไม่อยู่ใน 3 อันดับ"
        )
        fig_map = create_choropleth_map(
            map_data,
            geojson=geojson_data,
            location_col="region",
            color_col="unemployment_rate",
            title=f"อัตราการว่างงานรายจังหวัด (ปี {eval_year})",
            subtitle="หน่วย: ร้อยละของกำลังแรงงาน (สศช. HAI Databook ตารางที่ 9 สำรวจโดย สสช.)",
            color_scale="YlOrRd",
            hover_name="region",
            hover_data={"unemployment_rate": ":.2f", "สถานะ": True},
            labels={"unemployment_rate": "อัตราว่างงาน (%)", "สถานะ": "สถานะรายงานปัญหา"}
        )
        st.plotly_chart(fig_map, use_container_width=True)
        render_source_footer(["unemployment", "map"])

    with col_box:
        # Box Plot แสดงการกระจายตัวของอัตราว่างงาน
        box_data = prov_filtered.copy()
        box_data["สถานะการรายงาน"] = box_data["has_employment_problem"].apply(
            lambda x: "รายงานปัญหาใน 3 อันดับ" if x == 1 else "ไม่อยู่ใน 3 อันดับ"
        )
        box_data["ปี พ.ศ."] = box_data["year"].astype(str)
        
        # กรองปีตาม Global Context
        if global_year != "ทั้งสองปี":
            box_data = box_data[box_data["year"] == int(global_year)]
            fig_box = create_box_plot(
                box_data,
                x_col="สถานะการรายงาน",
                y_col="unemployment_rate",
                title=f"การกระจายตัวของอัตราการว่างงาน ปี {global_year}",
                subtitle="Box Plot พร้อมจุดข้อมูลจริงของแต่ละจังหวัด",
                x_label="สถานะการรายงานปัญหาอาชีพ",
                y_label="อัตราการว่างงาน (%)",
                color_col="สถานะการรายงาน",
                color_discrete_map=STATUS_COLORS
            )
        else:
            # ทั้งสองปี: แสดงแยกสถานะและปี
            fig_box = go.Figure()
            for yr in [2566, 2567]:
                sub_yr = box_data[box_data["year"] == yr]
                for st_name, color in [("รายงานปัญหาใน 3 อันดับ", STATUS_COLORS["รายงานปัญหา"]), ("ไม่อยู่ใน 3 อันดับ", STATUS_COLORS["ไม่อยู่ใน 3 อันดับ"])]:
                    pts = sub_yr[sub_yr["สถานะการรายงาน"] == st_name]
                    fig_box.add_trace(go.Box(
                        x=[f"{st_name}\n({yr})"] * len(pts),
                        y=pts["unemployment_rate"],
                        name=f"{st_name} ({yr})",
                        marker_color=color,
                        boxpoints="all",
                        jitter=0.3,
                        pointpos=-1.8,
                        hovertext=pts["region"],
                        hovertemplate="<b>%{hovertext}</b><br>อัตราว่างงาน: %{y:.2f}%<extra></extra>"
                    ))
            fig_box.update_layout(height=420, showlegend=False)
            fig_box = apply_plotly_theme(
                fig_box,
                title="การกระจายตัวของอัตราการว่างงาน เปรียบเทียบปี 2566 และ 2567",
                subtitle="Box Plot แยกตามสถานะรายงานปัญหาและปี (หนึ่งจุดต่อจังหวัด-ปี)",
                x_title="กลุ่มสถานะและปี",
                y_title="อัตราการว่างงาน (%)"
            )
        st.plotly_chart(fig_box, use_container_width=True)
        render_source_footer(["unemployment"])

    # 3. Dumbbell Chart / ส่วนต่างการเปลี่ยนแปลงรายจังหวัด
    st.markdown("#### 📈 การเปลี่ยนแปลงอัตราการว่างงานรายจังหวัดระหว่างปี 2566 และ 2567 (หน่วย: จุดเปอร์เซ็นต์)")
    
    # Pivot เพื่อหาค่าว่างงานปี 2566 และ 2567 ต่อจังหวัด
    piv = prov_filtered.pivot(index="region", columns="year", values="unemployment_rate").dropna()
    piv["diff_ppt"] = piv[2567] - piv[2566]
    piv = piv.reset_index()

    # ควบคุมจำนวนจังหวัดที่แสดงใน Dumbbell Chart เพื่อความสวยงามและอ่านง่าย
    col_ctrl1, col_ctrl2 = st.columns([1, 1])
    top_n = col_ctrl1.slider("จำนวนจังหวัดที่แสดงในกราฟเปรียบเทียบ:", min_value=10, max_value=len(piv), value=min(20, len(piv)), key="t3_top_n")
    sort_mode = col_ctrl2.radio(
        "เรียงลำดับตาม:",
        ["อัตราว่างงานเพิ่มขึ้นมากที่สุด (Positive diff)", "อัตราว่างงานลดลงมากที่สุด (Negative diff)", "อัตราว่างงานปี 2567 สูงสุด"],
        index=0,
        horizontal=True,
        key="t3_sort_mode"
    )

    if sort_mode == "อัตราว่างงานเพิ่มขึ้นมากที่สุด (Positive diff)":
        piv_plot = piv.sort_values(by="diff_ppt", ascending=False).head(top_n).sort_values(by="diff_ppt", ascending=True)
    elif sort_mode == "อัตราว่างงานลดลงมากที่สุด (Negative diff)":
        piv_plot = piv.sort_values(by="diff_ppt", ascending=True).head(top_n).sort_values(by="diff_ppt", ascending=False)
    else:
        piv_plot = piv.sort_values(by=2567, ascending=False).head(top_n).sort_values(by=2567, ascending=True)

    # สร้าง Dumbbell Chart
    fig_dumb = go.Figure()
    
    # เส้นเชื่อมระหว่างจุด 2566 และ 2567
    for _, row in piv_plot.iterrows():
        line_color = "#EF4444" if row["diff_ppt"] > 0 else "#10B981"
        fig_dumb.add_trace(go.Scatter(
            x=[row[2566], row[2567]],
            y=[row["region"], row["region"]],
            mode="lines",
            line={"color": line_color, "width": 2},
            showlegend=False,
            hoverinfo="none"
        ))

    # จุดปี 2566
    fig_dumb.add_trace(go.Scatter(
        x=piv_plot[2566],
        y=piv_plot["region"],
        mode="markers",
        name="ปี 2566",
        marker={"color": YEAR_COLORS[2566], "size": 9},
        hovertemplate="<b>%{y} (2566)</b><br>อัตราว่างงาน: %{x:.2f}%<extra></extra>"
    ))

    # จุดปี 2567
    fig_dumb.add_trace(go.Scatter(
        x=piv_plot[2567],
        y=piv_plot["region"],
        mode="markers",
        name="ปี 2567",
        marker={"color": YEAR_COLORS[2567], "size": 10, "symbol": "diamond"},
        hovertemplate="<b>%{y} (2567)</b><br>อัตราว่างงาน: %{x:.2f}%<extra></extra>"
    ))

    fig_dumb.update_layout(
        height=max(400, top_n * 22),
        legend={"orientation": "h", "y": 1.05, "x": 0.5, "xanchor": "center"}
    )
    fig_dumb = apply_plotly_theme(
        fig_dumb,
        title=f"เปรียบเทียบอัตราการว่างงานรายจังหวัด ปี 2566 เทียบ ปี 2567 ({len(piv_plot)} จังหวัด)",
        subtitle="Dumbbell Chart: เส้นสีแดง = ว่างงานเพิ่มขึ้น (ppt), เส้นสีเขียว = ว่างงานลดลง (ppt)",
        x_title="อัตราการว่างงาน (%)",
        y_title="จังหวัด"
    )
    st.plotly_chart(fig_dumb, use_container_width=True)
    render_source_footer(["unemployment"])

    # 4. ตารางเจาะลึกรายละเอียด
    st.markdown("#### 📄 ตารางรายละเอียดความต้องการด้านอาชีพและอัตราการว่างงาน 2 ปี")
    
    emp_main = main_df[
        (main_df["region"] != "ทั่วประเทศ") &
        (main_df["problem_group"] == "อาชีพและการจ้างงาน")
    ].copy()

    if global_year != "ทั้งสองปี":
        emp_main = emp_main[emp_main["year"] == int(global_year)]
    if global_provinces:
        emp_main = emp_main[emp_main["region"].isin(global_provinces)]
    if selected_sub != "ทั้งหมด":
        emp_main = emp_main[emp_main["standard_problem"] == selected_sub]

    # รวมค่าว่างงานทั้งสองปี
    unemp_map_66 = province_df[province_df["year"] == 2566].set_index("region")["unemployment_rate"].to_dict()
    unemp_map_67 = province_df[province_df["year"] == 2567].set_index("region")["unemployment_rate"].to_dict()

    emp_main["ว่างงาน_2566"] = emp_main["region"].map(unemp_map_66)
    emp_main["ว่างงาน_2567"] = emp_main["region"].map(unemp_map_67)
    emp_main["ส่วนต่าง_ppt"] = emp_main["ว่างงาน_2567"] - emp_main["ว่างงาน_2566"]

    display_emp = emp_main[[
        "year", "region", "Need", "standard_problem", "Per_vill", "ว่างงาน_2566", "ว่างงาน_2567", "ส่วนต่าง_ppt"
    ]].copy()
    display_emp.columns = [
        "ปี พ.ศ.", "จังหวัด", "อันดับ", "ปัญหาย่อย", "ร้อยละหมู่บ้าน (%)",
        "อัตราว่างงาน 2566 (%)", "อัตราว่างงาน 2567 (%)", "ส่วนต่าง (จุดเปอร์เซ็นต์ ppt)"
    ]

    st.dataframe(
        display_emp.sort_values(by=["ปี พ.ศ.", "จังหวัด", "อันดับ"]),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"แสดงข้อมูลทั้งหมด {len(display_emp):,} รายการ")
