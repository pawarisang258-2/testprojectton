"""
tab2_province_reality.py
แท็บ 2: เจาะลึกรายจังหวัดและ Reality Check (Provincial Deep-Dive) — Halloween Edition
เริ่มต้นด้วยข้อความ 'กรุณาเลือกจังหวัด' รองรับการกรองภูมิภาคก่อน และแสดงผลแบบ Split Screen
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from src.components import (
    render_kpi_halloween,
    render_source_footer,
    render_empty_state_halloween
)
from src.theme import (
    GROUP_COLORS_9,
    FONT_FAMILY,
    apply_plotly_dark_theme
)


def render_tab2(main_df, province_df, geojson_data, global_filters):
    """
    เรนเดอร์เนื้อหา Tab 2: เจาะลึกรายจังหวัดและ Reality Check
    """
    st.markdown("### 👻 เจาะลึกรายจังหวัด & Reality Check (Provincial Deep-Dive)")
    st.markdown(
        "สำรวจความต้องการ 3 อันดับแรกของจังหวัด และเปรียบเทียบกับ **ข้อมูลบริบทเสริมจริง** "
        "(ค่าใช้จ่ายครัวเรือน อัตราการว่างงาน และผลผลิตข้าวนาปี) "
        "โดยปราศจาก Mock Data, Truth Score หรือคะแนนสมมติใด ๆ"
    )

    # 1. แถบควบคุมการเลือกจังหวัด (Dropdown + กรองภูมิภาค)
    st.markdown(
        "<div style='background:rgba(20,20,35,0.85); border:1px solid rgba(138,43,226,0.35); border-radius:14px; padding:18px 22px; margin-bottom:20px;'>"
        "<div style='color:#FF9E4A; font-weight:700; font-size:1.05rem; margin-bottom:12px;'>🔮 เลือกจังหวัดเพื่อเข้าสู่ Provincial Deep-Dive</div>",
        unsafe_allow_html=True
    )

    col_c1, col_c2, col_c3 = st.columns([1, 1.2, 1.2])
    
    # เลือกระดับปี
    selected_year = col_c1.radio(
        "📅 เลือกปีการสำรวจ:",
        ["2567 (ล่าสุด)", "2566"],
        index=0 if global_filters["year"] in ["2567", "ทั้งหมด"] else 1,
        horizontal=True,
        key="t2_year_radio"
    )
    selected_year_int = 2567 if "2567" in selected_year else 2566

    # เลือกภูมิภาคก่อน
    all_regions = ["🌐 ทุกภูมิภาค (77 จังหวัด)"] + sorted(
        main_df[main_df["region"] != "ทั่วประเทศ"]["region_group"].dropna().unique().tolist()
    )
    chosen_region = col_c2.selectbox("🏰 กรองตามภูมิภาค:", all_regions, index=0, key="t2_region_select")

    # กรองรายชื่อจังหวัดตามภูมิภาค
    prov_pool = main_df[main_df["region"] != "ทั่วประเทศ"]
    if chosen_region != "🌐 ทุกภูมิภาค (77 จังหวัด)":
        prov_pool = prov_pool[prov_pool["region_group"] == chosen_region]
    available_provinces = sorted(prov_pool["region"].unique().tolist())

    # ตัวเลือกจังหวัด โดยมีค่าเริ่มต้นเป็น 'กรุณาเลือกจังหวัด'
    province_options = ["-- กรุณาเลือกจังหวัด --"] + available_provinces
    
    # หากผู้ใช้คลิกเลือกปุ่มจังหวัดแนะนำ
    if "quick_pick_province" in st.session_state and st.session_state["quick_pick_province"] in province_options:
        curr_idx = province_options.index(st.session_state["quick_pick_province"])
    else:
        curr_idx = 0

    target_province = col_c3.selectbox(
        "📍 ค้นหาและเลือกจังหวัด:",
        options=province_options,
        index=curr_idx,
        key="t2_province_dropdown"
    )

    # ปุ่มทางลัดเลือกจังหวัดแนะนำ (Quick Pick Buttons ตามแบบเพื่อน)
    st.markdown("<div style='font-size:0.85rem; color:#CBD5E1; margin-top:8px; margin-bottom:6px;'>🎃 จังหวัดแนะนำ (คลิกเพื่อเลือกทันที):</div>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4, p_col5, p_col6 = st.columns(6)
    
    if p_col1.button("เชียงใหม่ (เหนือ)", use_container_width=True):
        st.session_state["quick_pick_province"] = "เชียงใหม่"
        st.rerun()
    if p_col2.button("ขอนแก่น (อีสาน)", use_container_width=True):
        st.session_state["quick_pick_province"] = "ขอนแก่น"
        st.rerun()
    if p_col3.button("กรุงเทพมหานคร (กลาง)", use_container_width=True):
        st.session_state["quick_pick_province"] = "กรุงเทพมหานคร"
        st.rerun()
    if p_col4.button("สุราษฎร์ธานี (ใต้)", use_container_width=True):
        st.session_state["quick_pick_province"] = "สุราษฎร์ธานี"
        st.rerun()
    if p_col5.button("ชลบุรี (ตะวันออก)", use_container_width=True):
        st.session_state["quick_pick_province"] = "ชลบุรี"
        st.rerun()
    if p_col6.button("กาญจนบุรี (ตะวันตก)", use_container_width=True):
        st.session_state["quick_pick_province"] = "กาญจนบุรี"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # ตรวจสอบว่าผู้ใช้เลือกจังหวัดแล้วหรือยัง
    # =========================================================================
    if target_province == "-- กรุณาเลือกจังหวัด --":
        # แสดงคำแนะนำเริ่มต้นตามข้อกำหนด (เมื่อยังไม่เลือกจังหวัด)
        guide_html = (
            "<div style='background:rgba(22,22,38,0.85); border:1px solid rgba(138,43,226,0.3); border-radius:16px; padding:36px; text-align:center; margin-top:14px;'>"
            "<div style='font-size:3rem; margin-bottom:12px;'>👈 🗺️</div>"
            "<h3 style='color:#FF9E4A; margin-bottom:8px; font-weight:700;'>กรุณาเลือกจังหวัดเพื่อดูผลวิเคราะห์เจาะลึก</h3>"
            "<p style='color:#CBD5E1; max-width:650px; margin:0 auto 18px auto; line-height:1.6; font-size:0.95rem;'>"
            "ท่านสามารถพิมพ์ชื่อจังหวัดในช่องค้นหาด้านบน หรือคลิกปุ่มจังหวัดแนะนำเพื่อเริ่มต้นการสำรวจ<br>"
            "ระบบจะแสดง <b>3 อันดับแรกของความต้องการ</b> (รวมอันดับเสมอ) คู่ขนานกับ <b>ข้อมูลบริบทเสริมจริง</b> ในรูปแบบ Split Screen"
            "</p>"
            "<div style='display:inline-block; background:rgba(138,43,226,0.25); border:1px solid #8A2BE2; padding:6px 18px; border-radius:20px; font-size:0.85rem; color:#E9D5FF;'>"
            "💡 รองรับครบทั้ง 77 จังหวัด และใช้เฉพาะข้อมูลที่ตรวจสอบได้จริง"
            "</div>"
            "</div>"
        )
        st.markdown(guide_html, unsafe_allow_html=True)
        return

    # =========================================================================
    # เมื่อเลือกจังหวัดแล้ว: แสดงผลแบบ Split Screen 2 ฝั่ง
    # =========================================================================
    prov_needs = main_df[
        (main_df["region"] == target_province) &
        (main_df["year"] == selected_year_int)
    ].sort_values(by="Need")

    prov_metrics = province_df[
        (province_df["region"] == target_province) &
        (province_df["year"] == selected_year_int)
    ]
    reg_name = main_df[main_df["region"] == target_province]["region_group"].iloc[0] if not prov_needs.empty else ""

    col_left, col_right = st.columns([1, 1.15], gap="large")

    # -------------------------------------------------------------------------
    # ฝั่งซ้าย: รายการความต้องการอันดับ 1, 2, 3 (รวมอันดับเสมอ)
    # -------------------------------------------------------------------------
    with col_left:
        header_left = (
            f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>"
            f"<h4 style='margin:0; color:#FF6B00;'>📍 ความต้องการของ: {target_province} ({reg_name})</h4>"
            f"<span class='header-badge-halloween'>ปี พ.ศ. {selected_year_int}</span>"
            f"</div>"
        )
        st.markdown(header_left, unsafe_allow_html=True)

        if prov_needs.empty:
            render_empty_state_halloween(
                f"ไม่พบข้อมูลความต้องการของจังหวัด {target_province} ในปี {selected_year_int}",
                "กรุณาเปลี่ยนจังหวัดหรือปีการสำรวจ"
            )
        else:
            st.caption(f"พบรายการความต้องการทั้งหมด {len(prov_needs)} รายการ (คงอันดับร่วมและรายการเสมอตามจริง)")

            # สร้างการ์ดแสดงรายการความต้องการแต่ละอันดับ
            for idx, (_, row) in enumerate(prov_needs.iterrows()):
                need_rank = str(row["Need"])
                issue_text = str(row["Iss_Need"])
                group_name = str(row["Iss_Need_Grouped"])
                per_vill = float(row["Per_vill"])

                rank_class = "rank-1" if "1" in need_rank else ("rank-2" if "2" in need_rank else "rank-3")
                badge_class = "badge-rank-1" if "1" in need_rank else ("badge-rank-2" if "2" in need_rank else "badge-rank-3")
                group_color = GROUP_COLORS_9.get(group_name, "#FF6B00")

                card_html = (
                    f"<div class='rank-card {rank_class}'>"
                    f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                    f"<span class='rank-badge {badge_class}'>{need_rank}</span>"
                    f"<span style='font-size:0.82rem; color:{group_color}; font-weight:600;'>● {group_name}</span>"
                    f"</div>"
                    f"<div style='font-size:1.15rem; font-weight:600; color:#FFFFFF; margin:6px 0 4px 0;'>"
                    f"{issue_text}"
                    f"</div>"
                    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-top:8px;'>"
                    f"<span style='font-size:0.85rem; color:#CBD5E1;'>ร้อยละหมู่บ้าน/ชุมชนที่รายงาน:</span>"
                    f"<span style='font-size:1.2rem; font-weight:700; color:#FF9E4A;'>{per_vill:.1f}%</span>"
                    f"</div>"
                    f"<div style='background:rgba(255,255,255,0.08); border-radius:6px; height:8px; overflow:hidden; margin-top:6px;'>"
                    f"<div style='background:linear-gradient(90deg, #8A2BE2, #FF6B00); width:{min(100, max(5, per_vill))}%; height:100%; border-radius:6px;'></div>"
                    f"</div>"
                    f"</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

            with st.expander("📋 ดูข้อมูลตารางความต้องการของจังหวัดนี้", expanded=False):
                st.dataframe(
                    prov_needs[["Need", "Iss_Need", "Iss_Need_Grouped", "Per_vill"]].rename(
                        columns={
                            "Need": "อันดับ",
                            "Iss_Need": "ข้อความระบุปัญหา",
                            "Iss_Need_Grouped": "กลุ่มปัญหา 9 กลุ่ม",
                            "Per_vill": "ร้อยละหมู่บ้าน (%)"
                        }
                    ),
                    hide_index=True,
                    use_container_width=True
                )
            render_source_footer(["main"])

    # -------------------------------------------------------------------------
    # ฝั่งขวา: Reality Check & ข้อมูลบริบทเสริมจริง (Verified Indicators)
    # -------------------------------------------------------------------------
    with col_right:
        header_right = (
            f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>"
            f"<h4 style='margin:0; color:#00FF66;'>🔮 Reality Check: ข้อมูลบริบทเสริมจริง</h4>"
            f"<span class='header-badge-halloween' style='border-color:#00FF66; color:#86EFAC;'>Verified Indicators</span>"
            f"</div>"
        )
        st.markdown(header_right, unsafe_allow_html=True)

        selected_indicator = st.selectbox(
            "เลือกตัวชี้วัดบริบทเสริมเพื่อวิเคราะห์ความสอดคล้อง:",
            [
                "ค่าใช้จ่ายเฉลี่ยครัวเรือนต่อเดือน (ปี 2567)",
                "อัตราการว่างงานของกำลังแรงงาน (ปี 2566–2567)",
                "ผลผลิตข้าวนาปีต่อเนื้อที่เก็บเกี่ยว (ปี 2567)"
            ],
            index=0,
            key="t2_reality_indicator"
        )

        exp_val = prov_metrics["monthly_expenditure"].values[0] if not prov_metrics.empty and "monthly_expenditure" in prov_metrics else None
        unemp_val = prov_metrics["unemployment_rate"].values[0] if not prov_metrics.empty and "unemployment_rate" in prov_metrics else None
        rice_val = prov_metrics["rice_yield_per_rai"].values[0] if not prov_metrics.empty and "rice_yield_per_rai" in prov_metrics else None

        # ---------------------------------------------------------------------
        # 1. ค่าใช้จ่ายครัวเรือน
        # ---------------------------------------------------------------------
        if "ค่าใช้จ่าย" in selected_indicator:
            if selected_year_int == 2566:
                render_empty_state_halloween(
                    "ไม่มีข้อมูลค่าใช้จ่ายครัวเรือนสำหรับปี 2566",
                    "การสำรวจภาวะเศรษฐกิจและสังคมของครัวเรือน (สสช.) มีเฉพาะปี 2567 เท่านั้น ระบบไม่นำค่าปี 2567 มาเติมย้อนหลัง"
                )
            else:
                p67 = province_df[province_df["year"] == 2567].dropna(subset=["monthly_expenditure"])
                nat_mean_exp = p67["monthly_expenditure"].mean()
                reg_mean_exp = p67[p67["region_group"] == reg_name]["monthly_expenditure"].mean()

                prov_exp_disp = f"{exp_val:,.2f} บาท" if pd.notna(exp_val) else "ไม่มีข้อมูล"
                diff_nat = (exp_val - nat_mean_exp) if pd.notna(exp_val) else 0
                n_reg_exp = len(p67[p67["region_group"] == reg_name])

                kpi_right_html = (
                    f"<div class='kpi-container'>"
                    f"{render_kpi_halloween(f'ค่าใช้จ่าย: {target_province}', prov_exp_disp, f'ส่วนต่างเฉลี่ยประเทศ: {diff_nat:+,.1f} บาท', 'orange')}"
                    f"{render_kpi_halloween(f'เฉลี่ยกลุ่ม {reg_name}', f'{reg_mean_exp:,.2f} บาท', f'n = {n_reg_exp} จังหวัด', 'purple')}"
                    f"{render_kpi_halloween('เฉลี่ยทั้งประเทศ (77 จ.)', f'{nat_mean_exp:,.2f} บาท', 'ค่าเฉลี่ยไม่ถ่วงน้ำหนัก', 'cyan')}"
                    f"</div>"
                )
                st.markdown(kpi_right_html, unsafe_allow_html=True)

                comp_exp_df = pd.DataFrame({
                    "พื้นที่": [f"จ. {target_province}", f"เฉลี่ย {reg_name}", "เฉลี่ยทั้งประเทศ"],
                    "ค่าใช้จ่ายเฉลี่ย (บาท/เดือน)": [exp_val, reg_mean_exp, nat_mean_exp],
                    "สี": ["#FF6B00", "#8A2BE2", "#00F5D4"]
                })
                fig_exp = go.Figure()
                fig_exp.add_trace(go.Bar(
                    x=comp_exp_df["พื้นที่"],
                    y=comp_exp_df["ค่าใช้จ่ายเฉลี่ย (บาท/เดือน)"],
                    marker_color=comp_exp_df["สี"],
                    text=[f"{v:,.0f} บ." if pd.notna(v) else "-" for v in comp_exp_df["ค่าใช้จ่ายเฉลี่ย (บาท/เดือน)"]],
                    textposition="outside",
                    textfont={"color": "#FFFFFF", "size": 12, "family": FONT_FAMILY}
                ))
                fig_exp = apply_plotly_dark_theme(
                    fig_exp,
                    title=f"เปรียบเทียบค่าใช้จ่ายครัวเรือน: {target_province} เทียบกลุ่มพื้นที่ (ปี 2567)",
                    subtitle="หน่วย: บาท/ครัวเรือน/เดือน (การสำรวจภาวะเศรษฐกิจและสังคมของครัวเรือน สสช.)",
                    y_title="ค่าใช้จ่าย (บาท/เดือน)"
                )
                fig_exp.update_layout(height=360, showlegend=False)
                st.plotly_chart(fig_exp, use_container_width=True)

                note_html = (
                    f"<div style='font-size:0.83rem; color:#CBD5E1; line-height:1.5; background:rgba(20,20,35,0.7); padding:12px 14px; border-radius:10px; border-left:3px solid #FF6B00;'>"
                    f"💡 <b>ข้อสังเกตเชิงบริบท:</b> หากจังหวัดรายงานปัญหาด้าน <i>'ค่าครองชีพและราคาสินค้า'</i> หรือ <i>'หนี้สินและแหล่งเงินทุน'</i> ในอันดับต้น ๆ "
                    f"การมีค่าใช้จ่ายครัวเรือนที่สูงกว่าค่าเฉลี่ยอาจสะท้อนแรงกดดันด้านค่าครองชีพในพื้นที่ อย่างไรก็ดี เป็นเพียงบริบทเสริม ไม่สามารถสรุปความสัมพันธ์เชิงเหตุและผลได้"
                    f"</div>"
                )
                st.markdown(note_html, unsafe_allow_html=True)
                render_source_footer(["expenditure"])

        # ---------------------------------------------------------------------
        # 2. อัตราการว่างงาน
        # ---------------------------------------------------------------------
        elif "อัตราการว่างงาน" in selected_indicator:
            p_unemp = province_df[province_df["year"] == selected_year_int].dropna(subset=["unemployment_rate"])
            nat_mean_unemp = p_unemp["unemployment_rate"].mean()
            reg_mean_unemp = p_unemp[p_unemp["region_group"] == reg_name]["unemployment_rate"].mean()

            p_prov_both = province_df[province_df["region"] == target_province].set_index("year")["unemployment_rate"].to_dict()
            u66 = p_prov_both.get(2566, None)
            u67 = p_prov_both.get(2567, None)
            u_diff = (u67 - u66) if u66 is not None and u67 is not None else 0

            kpi_unemp_html = (
                f"<div class='kpi-container'>"
                f"{render_kpi_halloween(f'อัตราว่างงาน: {target_province}', f'{unemp_val:.2f}%' if pd.notna(unemp_val) else '-', f'ปี 2566: {u66:.2f}% | ปี 2567: {u67:.2f}%', 'blood')}"
                f"{render_kpi_halloween(f'เฉลี่ยกลุ่ม {reg_name}', f'{reg_mean_unemp:.2f}%', f'ปี {selected_year_int} (ไม่ถ่วงน้ำหนัก)', 'purple')}"
                f"{render_kpi_halloween('การเปลี่ยนแปลง 2 ปี', f'{u_diff:+.2f} ppt', 'ส่วนต่าง 2566 ➔ 2567 (จุดเปอร์เซ็นต์)', 'green')}"
                f"</div>"
            )
            st.markdown(kpi_unemp_html, unsafe_allow_html=True)

            comp_unemp_df = pd.DataFrame({
                "พื้นที่": [f"จ. {target_province}", f"เฉลี่ย {reg_name}", "เฉลี่ยทั้งประเทศ"],
                "อัตราการว่างงาน (%)": [unemp_val, reg_mean_unemp, nat_mean_unemp],
                "สี": ["#FF0055", "#8A2BE2", "#00F5D4"]
            })
            fig_unemp = go.Figure()
            fig_unemp.add_trace(go.Bar(
                x=comp_unemp_df["พื้นที่"],
                y=comp_unemp_df["อัตราการว่างงาน (%)"],
                marker_color=comp_unemp_df["สี"],
                text=[f"{v:.2f}%" if pd.notna(v) else "-" for v in comp_unemp_df["อัตราการว่างงาน (%)"]],
                textposition="outside",
                textfont={"color": "#FFFFFF", "size": 12, "family": FONT_FAMILY}
            ))
            fig_unemp = apply_plotly_dark_theme(
                fig_unemp,
                title=f"เปรียบเทียบอัตราการว่างงาน: {target_province} เทียบกลุ่มพื้นที่ (ปี {selected_year_int})",
                subtitle="หน่วย: ร้อยละของกำลังแรงงาน (สศช. HAI Databook ตารางที่ 9 สำรวจโดย สสช.)",
                y_title="อัตราการว่างงาน (%)"
            )
            fig_unemp.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig_unemp, use_container_width=True)

            note_unemp_html = (
                f"<div style='font-size:0.83rem; color:#CBD5E1; line-height:1.5; background:rgba(20,20,35,0.7); padding:12px 14px; border-radius:10px; border-left:3px solid #00FF66;'>"
                f"💡 <b>ข้อสังเกตเชิงบริบท:</b> ปัญหา <i>'การส่งเสริมอาชีพ รายได้ และการจ้างงาน'</i> มีความกว้างกว่าเพียงอัตราการว่างงานในระบบทางการ "
                f"หมู่บ้าน/ชุมชนอาจต้องการการส่งเสริมอาชีพเสริมหรือเพิ่มรายได้ แม้ในพื้นที่ที่มีอัตราการว่างงานต่ำ"
                f"</div>"
            )
            st.markdown(note_unemp_html, unsafe_allow_html=True)
            render_source_footer(["unemployment"])

        # ---------------------------------------------------------------------
        # 3. ผลผลิตข้าวนาปี
        # ---------------------------------------------------------------------
        else:
            if selected_year_int == 2566:
                render_empty_state_halloween(
                    "ไม่มีข้อมูลผลผลิตข้าวนาปีสำหรับปี 2566",
                    "สถิติผลผลิตข้าวนาปีต่อเนื้อที่เก็บเกี่ยวในชุดข้อมูลนี้มีเฉพาะปี 2567 (สำนักงานเศรษฐกิจการเกษตร) ระบบไม่นำค่าปี 2567 มาทดแทนย้อนหลัง"
                )
            else:
                p_rice = province_df[province_df["year"] == 2567].dropna(subset=["rice_yield_per_rai"])
                nat_mean_rice = p_rice["rice_yield_per_rai"].mean()
                reg_mean_rice = p_rice[p_rice["region_group"] == reg_name]["rice_yield_per_rai"].mean()
                prov_rice_disp = f"{rice_val:,.1f} กก./ไร่" if pd.notna(rice_val) else "ไม่มีข้อมูล"
                diff_rice = (rice_val - nat_mean_rice) if pd.notna(rice_val) else 0
                n_reg_rice = len(p_rice[p_rice["region_group"] == reg_name])

                kpi_rice_html = (
                    f"<div class='kpi-container'>"
                    f"{render_kpi_halloween(f'ผลผลิตข้าว: {target_province}', prov_rice_disp, f'ส่วนต่างเฉลี่ยประเทศ: {diff_rice:+,.1f} กก./ไร่', 'green')}"
                    f"{render_kpi_halloween(f'เฉลี่ยกลุ่ม {reg_name}', f'{reg_mean_rice:,.1f} กก./ไร่', f'n = {n_reg_rice} จังหวัด', 'purple')}"
                    f"{render_kpi_halloween('เฉลี่ยทั้งประเทศ (77 จ.)', f'{nat_mean_rice:,.1f} กก./ไร่', 'ค่าเฉลี่ยไม่ถ่วงน้ำหนัก', 'cyan')}"
                    f"</div>"
                )
                st.markdown(kpi_rice_html, unsafe_allow_html=True)

                comp_rice_df = pd.DataFrame({
                    "พื้นที่": [f"จ. {target_province}", f"เฉลี่ย {reg_name}", "เฉลี่ยทั้งประเทศ"],
                    "ผลผลิตข้าว (กก./ไร่)": [rice_val, reg_mean_rice, nat_mean_rice],
                    "สี": ["#00FF66", "#8A2BE2", "#00F5D4"]
                })
                fig_rice = go.Figure()
                fig_rice.add_trace(go.Bar(
                    x=comp_rice_df["พื้นที่"],
                    y=comp_rice_df["ผลผลิตข้าว (กก./ไร่)"],
                    marker_color=comp_rice_df["สี"],
                    text=[f"{v:,.1f} กก." if pd.notna(v) else "-" for v in comp_rice_df["ผลผลิตข้าว (กก./ไร่)"]],
                    textposition="outside",
                    textfont={"color": "#FFFFFF", "size": 12, "family": FONT_FAMILY}
                ))
                fig_rice = apply_plotly_dark_theme(
                    fig_rice,
                    title=f"เปรียบเทียบผลผลิตข้าวนาปี: {target_province} เทียบกลุ่มพื้นที่ (ปี 2567)",
                    subtitle="หน่วย: กิโลกรัมต่อไร่ของเนื้อที่เก็บเกี่ยว (สำนักงานเศรษฐกิจการเกษตร)",
                    y_title="ผลผลิตข้าวนาปี (กก./ไร่)"
                )
                fig_rice.update_layout(height=360, showlegend=False)
                st.plotly_chart(fig_rice, use_container_width=True)

                note_rice_html = (
                    f"<div style='font-size:0.83rem; color:#CBD5E1; line-height:1.5; background:rgba(20,20,35,0.7); padding:12px 14px; border-radius:10px; border-left:3px solid #00F5D4;'>"
                    f"💡 <b>ข้อสังเกตเชิงบริบท:</b> ผลผลิตข้าวนาปีต่อไร่สะท้อนมิติด้านประสิทธิภาพผลผลิตต่อพื้นที่เก็บเกี่ยว "
                    f"แต่ไม่ครอบคลุมราคาพืชผลหรือต้นทุนปุ๋ยยา ดังนั้นเกษตรกรอาจยังเผชิญปัญหา <i>'ราคาสินค้าเกษตรและปัจจัยการผลิต'</i> ได้แม้ในพื้นที่ที่ผลผลิตต่อไร่สูง"
                    f"</div>"
                )
                st.markdown(note_rice_html, unsafe_allow_html=True)
                render_source_footer(["rice"])
