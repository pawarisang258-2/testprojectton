"""
theme.py
การกำหนดชุดสี ธีมการแสดงผล CSS และสไตล์มาตรฐานสำหรับ Plotly & Streamlit
"""

# สีประจำกลุ่มปัญหา 6 กลุ่มมาตรฐาน (ใช้เหมือนกันทุกกราฟเพื่อความคงเส้นคงวา)
GROUP_COLORS = {
    "เศรษฐกิจและการเงิน": "#2563EB",         # Royal Blue
    "เกษตรกรรมและที่ดิน": "#059669",         # Emerald Green
    "อาชีพและการจ้างงาน": "#D97706",         # Warm Amber
    "สาธารณูปโภคและโครงสร้างพื้นฐาน": "#0284C7", # Sky Blue
    "ความปลอดภัยและยาเสพติด": "#DC2626",      # Crimson Red
    "สิ่งแวดล้อมและภัยธรรมชาติ": "#0D9488",    # Teal
}

# สีสำหรับสถานะการรายงานปัญหา
STATUS_COLORS = {
    "รายงานปัญหา": "#1D4ED8",          # Deep Blue
    "รายงานปัญหาใน 3 อันดับ": "#1D4ED8",
    "ไม่อยู่ใน 3 อันดับ": "#94A3B8",     # Cool Slate
    "ไม่รายงานปัญหา": "#94A3B8"
}

# สีสำหรับการเปรียบเทียบปี 2566 vs 2567
YEAR_COLORS = {
    2566: "#60A5FA",   # Sky Blue
    "2566": "#60A5FA",
    2567: "#1E3A8A",   # Deep Navy Blue
    "2567": "#1E3A8A"
}

# Font family ภาษาไทยและสากล
FONT_FAMILY = "Sarabun, Prompt, Segoe UI, sans-serif"

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=Sarabun:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sarabun', 'Prompt', sans-serif;
    }

    /* Main Dashboard Header */
    .dashboard-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #2563EB 100%);
        padding: 24px 32px;
        border-radius: 14px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.15);
    }
    .dashboard-header h1 {
        font-family: 'Prompt', sans-serif;
        color: #FFFFFF !important;
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 8px 0;
        letter-spacing: -0.02em;
    }
    .dashboard-header p {
        color: #E2E8F0;
        font-size: 0.98rem;
        margin: 0;
        line-height: 1.5;
    }
    .header-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* KPI Cards */
    .kpi-container {
        display: flex;
        gap: 14px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .kpi-card {
        flex: 1;
        min-width: 200px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #2563EB;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.12);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-family: 'Prompt', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }
    .kpi-subtitle {
        font-size: 0.8rem;
        color: #94A3B8;
        margin-top: 4px;
    }
    .kpi-card.emerald { border-top-color: #059669; }
    .kpi-card.amber { border-top-color: #D97706; }
    .kpi-card.purple { border-top-color: #7C3AED; }
    .kpi-card.navy { border-top-color: #1E3A8A; }

    /* Chart Container Box */
    .chart-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px 14px 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
    }

    /* Filter Panel */
    .filter-panel {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }

    /* Active Filter Chips */
    .filter-chip {
        display: inline-flex;
        align-items: center;
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1E40AF;
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 4px;
    }

    /* Source Note & Footnote */
    .source-footnote {
        font-size: 0.8rem;
        color: #64748B;
        border-left: 3px solid #94A3B8;
        padding-left: 10px;
        margin-top: 8px;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    .source-footnote a {
        color: #2563EB;
        text-decoration: none;
    }
    .source-footnote a:hover {
        text-decoration: underline;
    }

    /* Missing Data Banner */
    .missing-data-box {
        background: #FFFBEB;
        border: 1px solid #FCD34D;
        border-radius: 10px;
        padding: 18px 22px;
        color: #92400E;
        font-size: 0.95rem;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Streamlit Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Prompt', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 10px 18px;
        border-radius: 8px 8px 0 0;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EFF6FF !important;
        color: #1E40AF !important;
        border-bottom: 3px solid #2563EB !important;
    }
</style>
"""


def apply_plotly_theme(fig, title="", subtitle="", x_title="", y_title=""):
    """
    ปรับแต่ง Plotly Figure ให้มีสไตล์ Modern Academic ที่สวยงามและอ่านง่าย
    """
    title_text = f"<b>{title}</b>"
    if subtitle:
        title_text += f"<br><span style='font-size:12px; color:#64748B; font-weight:normal;'>{subtitle}</span>"

    fig.update_layout(
        title={
            "text": title_text,
            "x": 0.01,
            "xanchor": "left",
            "y": 0.96,
            "font": {"family": FONT_FAMILY, "size": 16, "color": "#0F172A"}
        },
        font={"family": FONT_FAMILY, "size": 12, "color": "#334155"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        margin={"l": 40, "r": 30, "t": 75 if subtitle else 55, "b": 45},
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "font_size": 12,
            "font_family": FONT_FAMILY,
            "bordercolor": "#CBD5E1"
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11}
        }
    )

    if x_title:
        fig.update_xaxes(
            title_text=x_title,
            title_font={"size": 12, "color": "#475569"},
            showgrid=True,
            gridcolor="#F1F5F9",
            zeroline=False,
            tickfont={"size": 11}
        )
    else:
        fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", zeroline=False)

    if y_title:
        fig.update_yaxes(
            title_text=y_title,
            title_font={"size": 12, "color": "#475569"},
            showgrid=True,
            gridcolor="#F1F5F9",
            zeroline=False,
            tickfont={"size": 11}
        )
    else:
        fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9", zeroline=False)

    return fig
