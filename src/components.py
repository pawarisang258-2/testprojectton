"""
components.py
คอมโพเนนต์ส่วนกลางสำหรับสร้างกราฟ Plotly ธีม Halloween Dark Gothic, การ์ด KPI, แผนที่ และแหล่งที่มา
ฟอนต์: 'Prompt', sans-serif | สีความคมชัดสูง
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from src.theme import (
    GROUP_COLORS_9,
    STATUS_COLORS_HALLOWEEN,
    YEAR_COLORS_HALLOWEEN,
    FONT_FAMILY,
    apply_plotly_dark_theme
)

# ข้อความแหล่งที่มาทางการตาม BRD & HANDOFF
SOURCES = {
    "main": "สำนักงานสถิติแห่งชาติ (สสช.) กระทรวงดิจิทัลเพื่อเศรษฐกิจและสังคม — ข้อมูลความต้องการให้รัฐบาลช่วยเหลือของหมู่บ้าน/ชุมชน (https://data.go.th/dataset/0602_00_0002)",
    "expenditure": "สำนักงานสถิติแห่งชาติ (สสช.) — การสำรวจภาวะเศรษฐกิจและสังคมของครัวเรือน ปี 2567 (https://data.go.th/dataset/os_08_00009)",
    "unemployment": "สำนักงานสภาพัฒนาการเศรษฐกิจและสังคมแห่งชาติ (สศช.) ดัชนีความก้าวหน้าของคน (HAI Databook 2567 ตารางที่ 9) สำรวจโดย สสช.",
    "rice": "สำนักงานเศรษฐกิจการเกษตร (สศก.) กระทรวงเกษตรและสหกรณ์ — สถิติการปลูกข้าวนาปี ปี 2567 (https://catalog.oae.go.th/th/dataset/dataoae1104)",
    "map": "ขอบเขตแผนที่ 77 จังหวัด: OpenGISData-Thailand อ้างอิงกรมการปกครอง กระทรวงมหาดไทย"
}


def render_source_footer(sources_list):
    """แสดงแถบแหล่งอ้างอิงใต้กราฟ พร้อมลิงก์ที่เกี่ยวข้อง"""
    if isinstance(sources_list, str):
        sources_list = [sources_list]
    
    items = []
    for s in sources_list:
        text = SOURCES.get(s, s)
        items.append(f"• {text}")
    items_html = "<br>".join(items)
    html = f"<div class='source-footnote-halloween'><b>แหล่งที่มาของข้อมูล:</b><br>{items_html}</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state_halloween(message, tip=""):
    """แสดงกล่องข้อความเตือนเมื่อไม่มีข้อมูลตามเงื่อนไข (Empty State) โดยไม่ใช้ 4-space indentation"""
    tip_html = f"<div style='font-size:0.85rem; margin-top:4px; color:#FED7AA;'>{tip}</div>" if tip else ""
    html = f"<div class='missing-data-box-halloween'><span style='font-size:1.6rem;'>🎃</span><div><b style='color:#FF9E4A; font-size:1.05rem;'>{message}</b>{tip_html}</div></div>"
    st.markdown(html, unsafe_allow_html=True)


def render_kpi_halloween(title, value, subtitle="", card_type="orange"):
    """แสดง KPI Card ในรูปแบบ Glassmorphism Halloween (ไม่มี leading spaces เพื่อป้องกัน markdown code block)"""
    return f"<div class='kpi-card-halloween {card_type}'><div class='kpi-title-halloween'>{title}</div><div class='kpi-value-halloween'>{value}</div><div class='kpi-subtitle-halloween'>{subtitle}</div></div>"


def create_donut_chart_halloween(df, names_col, values_col, title, subtitle):
    """
    สร้าง Donut Chart แสดงสัดส่วนจำนวนรายการใน Top 3 (ระบุฐานการคำนวณชัดเจน)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 15, "color": "#CBD5E1"})
        return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle)

    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=0.55,
        color=names_col,
        color_discrete_map=GROUP_COLORS_9
    )
    total_val = df[values_col].sum()
    fig.update_traces(
        textinfo="percent+label",
        textposition="outside",
        textfont={"color": "#FFFFFF", "size": 11, "family": FONT_FAMILY},
        hovertemplate="<b>%{label}</b><br>จำนวนรายการ: %{value} รายการ<br>สัดส่วน: %{percent:.1%}<br><i>(คำนวณจากฐานรวม " + f"{total_val:,}" + " รายการที่บันทึก)</i><extra></extra>",
        marker={"line": {"width": 1.5, "color": "#07070B"}}
    )
    fig.update_layout(
        height=450,
        showlegend=False,
        annotations=[{
            "text": f"<b>{total_val:,}</b><br><span style='font-size:12px; color:#C084FC;'>รายการ</span>",
            "x": 0.5, "y": 0.5,
            "font": {"size": 19, "family": FONT_FAMILY, "color": "#FFFFFF"},
            "showarrow": False
        }]
    )
    return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle)


def create_treemap_halloween(df, path_cols, values_col, title, subtitle, color_col=None):
    """
    สร้าง Treemap ธีม Halloween แสดงเฉพาะ 9 กลุ่มปัญหาหลัก (ไม่มีการแตกปัญหาย่อยภายใน)
    ขนาดสี่เหลี่ยมสัมพันธ์กับจำนวนจังหวัดที่พบกลุ่มปัญหานั้นจริง
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 15, "color": "#CBD5E1"})
        return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle)

    fig = px.treemap(
        df,
        path=path_cols,
        values=values_col,
        color=color_col or path_cols[0],
        color_discrete_map=GROUP_COLORS_9
    )
    fig.update_traces(
        textinfo="label+value",
        textfont={"family": FONT_FAMILY, "size": 13, "color": "#FFFFFF"},
        hovertemplate="<b>%{label}</b><br>จำนวนจังหวัดที่รายงาน: %{value} จังหวัด<extra></extra>",
        marker={"line": {"width": 2, "color": "#07070B"}}
    )
    fig.update_layout(height=420)
    return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle)


def create_horizontal_bar_halloween(df, x_col, y_col, title, subtitle, x_label="", y_label=""):
    """
    สร้าง Horizontal Bar Chart สำหรับแสดงการจัดอันดับปัญหา (นับจำนวนจังหวัด)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 15, "color": "#CBD5E1"})
        return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)

    df_sorted = df.sort_values(by=x_col, ascending=True)

    fig = px.bar(
        df_sorted,
        x=x_col,
        y=y_col,
        orientation="h",
        color=y_col,
        color_discrete_map=GROUP_COLORS_9,
        text=x_col
    )
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        textfont={"color": "#FFFFFF", "size": 12, "family": FONT_FAMILY},
        hovertemplate="<b>%{y}</b><br>จำนวนจังหวัดที่รายงาน: %{x} จังหวัด<extra></extra>"
    )
    fig.update_layout(height=450, showlegend=False)
    return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)


def create_choropleth_map_halloween(df, geojson, location_col, color_col, title, subtitle,
                                    color_scale=None, color_discrete_map=None,
                                    hover_name=None, hover_data=None, labels=None, is_discrete=False):
    """
    สร้างแผนที่ Choropleth ของประเทศไทย 77 จังหวัดขนาดใหญ่ เต็มพื้นที่
    มีเส้นขอบจังหวัดสีสว่างชัดเจน (marker_line_width=1.0)
    และ fitbounds='geojson' เพื่อแสดงขอบเขตครบทุกจังหวัด
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 16, "color": "#CBD5E1"})
        return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle)

    if is_discrete:
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations=location_col,
            featureidkey="properties.pro_th",
            color=color_col,
            color_discrete_map=color_discrete_map or STATUS_COLORS_HALLOWEEN,
            hover_name=hover_name or location_col,
            hover_data=hover_data,
            labels=labels or {}
        )
    else:
        # Scale สีโทน Halloween: ม่วงลึก ➔ ม่วงนีออน ➔ ส้มฟักทอง ➔ เหลือง
        scale = color_scale or [
            [0, "#261E38"],
            [0.25, "#6D28D9"],
            [0.55, "#C026D3"],
            [0.8, "#EA580C"],
            [1, "#FF6B00"]
        ]
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations=location_col,
            featureidkey="properties.pro_th",
            color=color_col,
            color_continuous_scale=scale,
            hover_name=hover_name or location_col,
            hover_data=hover_data,
            labels=labels or {}
        )

    # ปรับเส้นขอบจังหวัดให้ชัดเจนบนพื้นหลังมืด
    fig.update_traces(
        marker_line_width=1.0,
        marker_line_color="rgba(255, 255, 255, 0.6)"
    )

    fig.update_geos(
        fitbounds="geojson",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
        projection_type="mercator"
    )

    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 60, "b": 10},
        height=720,
        coloraxis_colorbar={
            "tickfont": {"color": "#F1F5F9", "family": FONT_FAMILY},
            "title": {"font": {"color": "#F1F5F9", "family": FONT_FAMILY}}
        }
    )
    return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle)


def create_grouped_bar_halloween(df, x_col, y_col, color_col, title, subtitle, x_label="", y_label="",
                                color_discrete_map=None, text_auto=True, barmode="group"):
    """
    สร้าง Grouped Bar Chart เปรียบเทียบปี 2566 vs 2567
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 15, "color": "#CBD5E1"})
        return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        barmode=barmode,
        color_discrete_map=color_discrete_map or YEAR_COLORS_HALLOWEEN,
        text=y_col if text_auto else None
    )
    if text_auto:
        fig.update_traces(
            textposition="outside",
            cliponaxis=False,
            textfont={"color": "#FFFFFF", "size": 11, "family": FONT_FAMILY}
        )
    fig.update_layout(height=430)
    return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)


def create_multi_line_yoy_halloween(df, x_col, y_col, color_col, title, subtitle, x_label="ปี พ.ศ.", y_label="จำนวนจังหวัดที่รายงาน"):
    """
    สร้าง Interactive Multi-Line YoY Trend Chart สำหรับเปรียบเทียบ 9 กลุ่มปัญหา ระหว่างปี 2566 vs 2567
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 15, "color": "#CBD5E1"})
        return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)

    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        color_discrete_map=GROUP_COLORS_9,
        markers=True
    )
    fig.update_traces(
        line={"width": 3},
        marker={"size": 9, "line": {"width": 1.5, "color": "#FFFFFF"}},
        hovertemplate="<b>%{data.name}</b><br>ปี พ.ศ. %{x}: %{y} จังหวัด<extra></extra>"
    )
    fig.update_layout(
        height=430,
        xaxis={"type": "category", "tickfont": {"size": 13, "color": "#F8FAFC"}},
        legend={"orientation": "h", "y": -0.2, "x": 0.5, "xanchor": "center"}
    )
    return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)


def create_slope_chart_halloween(piv_df, title, subtitle):
    """
    สร้าง Overall Issue Slope / Trend Chart (ทิศทางความเปลี่ยนแปลงข้ามปี)
    เส้นสีแดง = พุ่งสูงขึ้น (Spike/Rising), เส้นสีม่วงอ่อน/เทา = ทรงตัวหรือลดลง
    """
    if piv_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 15, "color": "#CBD5E1"})
        return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle)

    fig = go.Figure()

    for _, row in piv_df.iterrows():
        name = row["Iss_Need_Grouped"]
        v66 = row[2566]
        v67 = row[2567]
        diff = row["diff_provinces"]
        
        # สีตามทิศทาง: พุ่งขึ้น = Blood Red (#FF0055), ลดลง/ทรงตัว = Witch Slate (#94A3B8 / #8A2BE2)
        line_color = "#FF0055" if diff > 0 else ("#00FF66" if diff < 0 else "#94A3B8")
        line_width = 3.5 if diff > 0 else 2.0

        # เพิ่มเส้นเชื่อม
        fig.add_trace(go.Scatter(
            x=["ปี 2566", "ปี 2567"],
            y=[v66, v67],
            mode="lines+markers+text",
            name=name,
            line={"color": line_color, "width": line_width},
            marker={"size": 8, "color": line_color},
            text=[f"{v66}", f"{v67} ({diff:+d})"],
            textposition=["middle left", "middle right"],
            textfont={"size": 11, "color": "#FFFFFF", "family": FONT_FAMILY},
            hovertemplate=f"<b>{name}</b><br>ปี 2566: {v66} จ.<br>ปี 2567: {v67} จ.<br>ผลต่าง: {diff:+d} จ.<extra></extra>"
        ))

    fig.update_layout(
        height=450,
        showlegend=False,
        xaxis={
            "type": "category",
            "tickfont": {"size": 13, "color": "#F8FAFC", "family": FONT_FAMILY},
            "showgrid": False
        },
        yaxis={
            "title_text": "จำนวนจังหวัดที่รายงาน (จังหวัด)",
            "title_font": {"size": 12, "color": "#CBD5E1"},
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.08)"
        }
    )
    return apply_plotly_dark_theme(fig, title=title, subtitle=subtitle)
