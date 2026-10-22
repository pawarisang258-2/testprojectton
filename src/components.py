"""
components.py
คอมโพเนนต์ส่วนกลางสำหรับสร้างกราฟ Plotly, การ์ด KPI, แผนที่ และข้อความระบุแหล่งที่มา
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from src.theme import (
    GROUP_COLORS,
    STATUS_COLORS,
    YEAR_COLORS,
    FONT_FAMILY,
    apply_plotly_theme
)

# ข้อความแหล่งที่มามาตรฐานตาม BRD & HANDOFF
SOURCES = {
    "main": "สำนักงานสถิติแห่งชาติ (สสช.) กระทรวงดิจิทัลเพื่อเศรษฐกิจและสังคม — ข้อมูลความต้องการให้รัฐบาลช่วยเหลือของหมู่บ้าน/ชุมชน (https://data.go.th/dataset/0602_00_0002)",
    "expenditure": "สำนักงานสถิติแห่งชาติ (สสช.) — การสำรวจภาวะเศรษฐกิจและสังคมของครัวเรือน ปี 2567 (https://data.go.th/dataset/os_08_00009)",
    "unemployment": "สศช. ดัชนีความก้าวหน้าของคน (HAI Databook 2567 ตารางที่ 9) อ้างอิงข้อมูลสำรวจภาวะการทำงานของประชากร สสช.",
    "rice": "สำนักงานเศรษฐกิจการเกษตร (สศก.) กระทรวงเกษตรและสหกรณ์ — สถิติการปลูกข้าวนาปี ปี 2567 (https://catalog.oae.go.th/th/dataset/dataoae1104)",
    "map": "ขอบเขตแผนที่ 77 จังหวัด: OpenGISData-Thailand อ้างอิงกรมการปกครองและกระทรวงมหาดไทย"
}


def render_source_footer(sources_list):
    """แสดงแถบแหล่งอ้างอิงใต้กราฟ พร้อมลิงก์ที่เกี่ยวข้อง"""
    if isinstance(sources_list, str):
        sources_list = [sources_list]
    
    html = "<div class='source-footnote'><b>แหล่งที่มาของข้อมูล:</b><br>"
    for s in sources_list:
        text = SOURCES.get(s, s)
        html += f"• {text}<br>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state(message, tip=""):
    """แสดงกล่องข้อความเมื่อไม่มีข้อมูลสำหรับปีหรือฟิลเตอร์ที่เลือก"""
    html = f"""
    <div class='missing-data-box'>
        <span style='font-size:1.5rem;'>⚠️</span>
        <div>
            <b>{message}</b>
            {f"<div style='font-size:0.85rem; margin-top:2px; color:#B45309;'>{tip}</div>" if tip else ""}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_kpi(title, value, subtitle="", card_type="blue"):
    """แสดง KPI Card ที่มีสไตล์สวยงาม"""
    html = f"""
    <div class='kpi-card {card_type}'>
        <div class='kpi-title'>{title}</div>
        <div class='kpi-value'>{value}</div>
        <div class='kpi-subtitle'>{subtitle}</div>
    </div>
    """
    return html


def create_choropleth_map(df, geojson, location_col, color_col, title, subtitle,
                          color_scale=None, color_discrete_map=None,
                          hover_name=None, hover_data=None, labels=None, is_discrete=False):
    """
    สร้างแผนที่ Choropleth ของประเทศไทย 77 จังหวัด
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 16})
        return apply_plotly_theme(fig, title=title, subtitle=subtitle)

    if is_discrete:
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations=location_col,
            featureidkey="properties.pro_th",
            color=color_col,
            color_discrete_map=color_discrete_map,
            hover_name=hover_name or location_col,
            hover_data=hover_data,
            labels=labels or {}
        )
    else:
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations=location_col,
            featureidkey="properties.pro_th",
            color=color_col,
            color_continuous_scale=color_scale or "Blues",
            hover_name=hover_name or location_col,
            hover_data=hover_data,
            labels=labels or {}
        )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator"
    )

    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 60, "b": 10},
        height=520
    )
    return apply_plotly_theme(fig, title=title, subtitle=subtitle)


def create_treemap(df, path_cols, values_col, title, subtitle, color_col=None, color_discrete_map=None):
    """
    สร้าง Treemap แสดงการกระจายตัวของกลุ่มปัญหา
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 16})
        return apply_plotly_theme(fig, title=title, subtitle=subtitle)

    fig = px.treemap(
        df,
        path=path_cols,
        values=values_col,
        color=color_col or path_cols[0],
        color_discrete_map=color_discrete_map or GROUP_COLORS
    )
    fig.update_traces(
        textinfo="label+value",
        hovertemplate="<b>%{label}</b><br>จำนวนจังหวัด: %{value} จังหวัด<extra></extra>",
        marker={"line": {"width": 1.5, "color": "#FFFFFF"}}
    )
    fig.update_layout(height=420)
    return apply_plotly_theme(fig, title=title, subtitle=subtitle)


def create_box_plot(df, x_col, y_col, title, subtitle, x_label="", y_label="", color_col=None, color_discrete_map=None):
    """
    สร้าง Box Plot พร้อมแสดงจุดข้อมูลจริงของทุกจังหวัด (All Points with Jitter)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 16})
        return apply_plotly_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)

    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        color=color_col or x_col,
        color_discrete_map=color_discrete_map or STATUS_COLORS,
        points="all",
        hover_name="region" if "region" in df.columns else None,
        hover_data=[y_col]
    )
    fig.update_layout(height=420, showlegend=False)
    return apply_plotly_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)


def create_grouped_bar(df, x_col, y_col, color_col, title, subtitle, x_label="", y_label="",
                       color_discrete_map=None, text_auto=True, barmode="group"):
    """
    สร้าง Bar Chart / Grouped Bar Chart เปรียบเทียบ
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 16})
        return apply_plotly_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        barmode=barmode,
        color_discrete_map=color_discrete_map or YEAR_COLORS,
        text=y_col if text_auto else None
    )
    if text_auto:
        fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=400)
    return apply_plotly_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)


def create_horizontal_bar(df, x_col, y_col, title, subtitle, x_label="", y_label="", color_col=None, color_discrete_map=None):
    """
    สร้าง Horizontal Bar Chart สำหรับแสดงการจัดอันดับปัญหา
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก", showarrow=False, font={"size": 16})
        return apply_plotly_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)

    # เรียงลำดับจากมากไปน้อย
    df_sorted = df.sort_values(by=x_col, ascending=True)

    fig = px.bar(
        df_sorted,
        x=x_col,
        y=y_col,
        orientation="h",
        color=color_col or y_col,
        color_discrete_map=color_discrete_map or GROUP_COLORS,
        text=x_col
    )
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>จำนวนจังหวัดที่รายงาน: %{x} จังหวัด<extra></extra>"
    )
    fig.update_layout(height=380, showlegend=False)
    return apply_plotly_theme(fig, title=title, subtitle=subtitle, x_title=x_label, y_title=y_label)
