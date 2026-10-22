"""
theme.py
การกำหนดชุดสี ธีมการแสดงผลแบบ Halloween Dark Gothic + Glassmorphism
และสไตล์มาตรฐานสำหรับ Plotly & Streamlit ตามแม่แบบ halloween_dashboard.html
ฟอนต์หลัก: 'Prompt', sans-serif | ฟอนต์ตกแต่งหัวข้อ: 'Creepster', cursive
"""

# สีประจำกลุ่มปัญหา 9 กลุ่มใหม่ (Halloween Gothic Palette)
GROUP_COLORS_9 = {
    "ค่าครองชีพและราคาสินค้า": "#FF6B00",             # Pumpkin Orange
    "ราคาสินค้าเกษตรและปัจจัยการผลิต": "#00FF66",        # Toxic Green
    "การส่งเสริมอาชีพ รายได้ และการจ้างงาน": "#FFD700",   # Ghost Gold
    "ความปลอดภัย สังคม และยาเสพติด": "#FF0055",      # Blood Red
    "เศรษฐกิจและสิ่งแวดล้อม": "#00F5D4",              # Ghost Cyan
    "การบริหารจัดการน้ำและภัยแล้ง": "#38BDF8",          # Eerie Water Blue
    "หนี้สินและแหล่งเงินทุน": "#B026FF",              # Neon Purple
    "โครงสร้างพื้นฐานและสาธารณูปโภค": "#FB923C",       # Lantern Amber
    "ที่ดินทำกินและเอกสารสิทธิ์": "#8A2BE2"           # Witch Purple
}

# สีสำหรับสถานะการรายงานปัญหา
STATUS_COLORS_HALLOWEEN = {
    "รายงานปัญหา": "#FF6B00",
    "รายงานปัญหาใน 3 อันดับ": "#FF6B00",
    "ไม่อยู่ใน 3 อันดับ": "#2A233D",
    "ไม่รายงานปัญหา": "#2A233D"
}

# สีสำหรับการเปรียบเทียบปี 2566 vs 2567
YEAR_COLORS_HALLOWEEN = {
    2566: "#8A2BE2",       # Witch Purple
    "2566": "#8A2BE2",
    2567: "#FF6B00",       # Pumpkin Orange
    "2567": "#FF6B00"
}

# Font family ตามที่ระบุใน halloween_dashboard.html ของเพื่อน
FONT_FAMILY = "'Prompt', sans-serif"

CUSTOM_CSS_HALLOWEEN = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&family=Prompt:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Prompt', sans-serif !important;
        background-color: #07070B !important;
        color: #F8FAFC !important;
    }

    /* Halloween Radial Gradients Background */
    .stApp {
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(138, 43, 226, 0.15) 0%, transparent 45%),
            radial-gradient(circle at 85% 80%, rgba(255, 107, 0, 0.15) 0%, transparent 45%),
            radial-gradient(circle at 50% 50%, rgba(0, 255, 102, 0.05) 0%, transparent 60%) !important;
        background-attachment: fixed !important;
    }

    /* ------------------------------------------------------------- */
    /* 1. Global Text Contrast Fixes (แก้ตัวหนังสือมืดให้อ่านชัด 100%) */
    /* ------------------------------------------------------------- */
    p, span, div, label, li, a {
        color: #F1F5F9;
    }
    
    /* Secondary & Caption Texts */
    .stCaption, [data-testid="stCaptionContainer"] p, small {
        color: #CBD5E1 !important;
        font-size: 0.88rem !important;
    }

    /* Sidebar Label & Text Contrast */
    section[data-testid="stSidebar"] {
        background-color: #0B0B14 !important;
        border-right: 1px solid rgba(138, 43, 226, 0.3) !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #FF9E4A !important;
        font-family: 'Prompt', sans-serif !important;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] label span,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #F8FAFC !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
    }
    section[data-testid="stSidebar"] p {
        color: #CBD5E1 !important;
    }

    /* Widget Labels across entire app */
    label[data-testid="stWidgetLabel"] p {
        color: #F8FAFC !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }

    /* Selectbox, Multiselect & Dropdown Styling (Readable Text when closed & open) */
    [data-baseweb="select"] {
        background-color: #121220 !important;
        border: 1px solid rgba(138, 43, 226, 0.5) !important;
        border-radius: 8px !important;
    }
    [data-baseweb="select"] div,
    [data-baseweb="select"] span {
        color: #FFFFFF !important;
        font-family: 'Prompt', sans-serif !important;
    }
    /* Dropdown Popover Menu (when open) */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {
        background-color: #151528 !important;
        color: #FFFFFF !important;
        font-family: 'Prompt', sans-serif !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: rgba(255, 107, 0, 0.25) !important;
        color: #FF9E4A !important;
    }
    div[data-baseweb="popover"] li[aria-selected="true"] {
        background-color: rgba(138, 43, 226, 0.35) !important;
        color: #00FF66 !important;
    }

    /* Multiselect Tags / Chips */
    [data-baseweb="tag"] {
        background-color: rgba(138, 43, 226, 0.4) !important;
        border: 1px solid #8A2BE2 !important;
        border-radius: 14px !important;
    }
    [data-baseweb="tag"] span {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }

    /* Radio Buttons & Checkboxes */
    [data-testid="stRadio"] label p,
    [data-testid="stRadio"] label span {
        color: #F8FAFC !important;
        font-size: 0.92rem !important;
    }

    /* Slider numbers and label */
    [data-testid="stSlider"] div,
    [data-testid="stSlider"] p,
    [data-testid="stSlider"] span {
        color: #F1F5F9 !important;
    }

    /* Text Input */
    [data-testid="stTextInput"] input {
        background-color: #121220 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(138, 43, 226, 0.5) !important;
        border-radius: 8px !important;
    }

    /* Expander header */
    [data-testid="stExpander"] summary span {
        color: #F8FAFC !important;
        font-weight: 600 !important;
    }

    /* ------------------------------------------------------------- */
    /* 2. Main Dashboard Header (Halloween Accent) */
    /* ------------------------------------------------------------- */
    .dashboard-header-halloween {
        background: rgba(16, 16, 28, 0.88);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(138, 43, 226, 0.45);
        border-radius: 16px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 0 30px rgba(138, 43, 226, 0.2);
        position: relative;
        overflow: hidden;
    }
    .dashboard-header-halloween::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #FF6B00, #8A2BE2, #00FF66, #FF0055);
    }
    .dashboard-header-halloween h1 {
        font-family: 'Prompt', sans-serif !important;
        color: #FF6B00 !important;
        font-size: 2.1rem;
        font-weight: 700;
        margin: 0 0 8px 0;
        text-shadow: 0 0 14px rgba(255, 107, 0, 0.65);
        letter-spacing: -0.01em;
    }
    .dashboard-header-halloween p {
        color: #E2E8F0 !important;
        font-size: 1rem;
        margin: 0;
        line-height: 1.5;
    }
    .header-badge-halloween {
        display: inline-block;
        background: rgba(138, 43, 226, 0.3);
        border: 1px solid #8A2BE2;
        color: #E9D5FF !important;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 10px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: 0 0 10px rgba(138, 43, 226, 0.4);
    }

    /* ------------------------------------------------------------- */
    /* 3. KPI Cards Glassmorphism */
    /* ------------------------------------------------------------- */
    .kpi-container {
        display: flex;
        gap: 16px;
        margin-bottom: 22px;
        flex-wrap: wrap;
    }
    .kpi-card-halloween {
        flex: 1;
        min-width: 200px;
        background: rgba(18, 18, 32, 0.88);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(138, 43, 226, 0.35);
        border-top: 4px solid #FF6B00;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);
        transition: all 0.25s ease;
    }
    .kpi-card-halloween:hover {
        transform: translateY(-3px);
        border-color: rgba(255, 107, 0, 0.7);
        box-shadow: 0 0 22px rgba(255, 107, 0, 0.3);
    }
    .kpi-title-halloween {
        font-size: 0.85rem;
        font-weight: 600;
        color: #CBD5E1 !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 6px;
    }
    .kpi-value-halloween {
        font-family: 'Prompt', sans-serif !important;
        font-size: 1.85rem;
        font-weight: 700;
        color: #FFFFFF !important;
        line-height: 1.2;
    }
    .kpi-subtitle-halloween {
        font-size: 0.84rem;
        color: #C084FC !important;
        margin-top: 6px;
    }
    .kpi-card-halloween.purple { border-top-color: #8A2BE2; }
    .kpi-card-halloween.green { border-top-color: #00FF66; }
    .kpi-card-halloween.cyan { border-top-color: #00F5D4; }
    .kpi-card-halloween.blood { border-top-color: #FF0055; }
    .kpi-card-halloween.gold { border-top-color: #FFD700; }

    /* ------------------------------------------------------------- */
    /* 4. Tab 2 Split-Screen Rank Cards & Reality Box */
    /* ------------------------------------------------------------- */
    .rank-card {
        background: rgba(22, 22, 38, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
        border-left: 5px solid #FF6B00;
        border-right: 1px solid rgba(138, 43, 226, 0.3);
        border-top: 1px solid rgba(138, 43, 226, 0.3);
        border-bottom: 1px solid rgba(138, 43, 226, 0.3);
        transition: all 0.25s ease;
    }
    .rank-card:hover {
        transform: translateX(4px);
        box-shadow: 0 0 18px rgba(255, 107, 0, 0.25);
    }
    .rank-card.rank-1 { border-left-color: #FF6B00; }
    .rank-card.rank-2 { border-left-color: #8A2BE2; }
    .rank-card.rank-3 { border-left-color: #FF0055; }
    
    .rank-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .badge-rank-1 { background: rgba(255, 107, 0, 0.25); color: #FF9E4A !important; border: 1px solid #FF6B00; }
    .badge-rank-2 { background: rgba(138, 43, 226, 0.25); color: #E9D5FF !important; border: 1px solid #8A2BE2; }
    .badge-rank-3 { background: rgba(255, 0, 85, 0.25); color: #FDA4AF !important; border: 1px solid #FF0055; }

    /* Filter Chips */
    .filter-chip-halloween {
        display: inline-flex;
        align-items: center;
        background: rgba(138, 43, 226, 0.2);
        border: 1px solid rgba(138, 43, 226, 0.6);
        color: #F1F5F9 !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 500;
        margin-right: 8px;
        margin-bottom: 6px;
    }

    /* Footnotes */
    .source-footnote-halloween {
        font-size: 0.82rem;
        color: #CBD5E1 !important;
        border-left: 3px solid #8A2BE2;
        padding-left: 10px;
        margin-top: 10px;
        margin-bottom: 14px;
        line-height: 1.5;
        background: rgba(18, 18, 30, 0.5);
        border-radius: 0 6px 6px 0;
        padding-top: 6px;
        padding-bottom: 6px;
    }
    .source-footnote-halloween a {
        color: #FF9E4A !important;
        text-decoration: underline;
    }

    /* Missing Data Banner */
    .missing-data-box-halloween {
        background: rgba(30, 20, 15, 0.9);
        border: 1px solid rgba(255, 107, 0, 0.6);
        border-radius: 12px;
        padding: 18px 22px;
        color: #FED7AA !important;
        font-size: 0.95rem;
        margin-bottom: 18px;
        box-shadow: 0 0 18px rgba(255, 107, 0, 0.2);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 2px solid rgba(138, 43, 226, 0.35);
        padding-bottom: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Prompt', sans-serif !important;
        font-weight: 600;
        font-size: 1.02rem;
        padding: 12px 22px;
        border-radius: 10px 10px 0 0;
        color: #CBD5E1 !important;
        background-color: rgba(22, 22, 38, 0.65) !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #FF6B00 !important;
        background-color: rgba(30, 30, 52, 0.85) !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(138, 43, 226, 0.3) !important;
        color: #FF6B00 !important;
        border: 1px solid rgba(255, 107, 0, 0.6) !important;
        border-bottom: 3px solid #FF6B00 !important;
        box-shadow: 0 0 18px rgba(255, 107, 0, 0.25) !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, rgba(138, 43, 226, 0.8), rgba(255, 107, 0, 0.8)) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        font-family: 'Prompt', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #8A2BE2, #FF6B00) !important;
        box-shadow: 0 0 18px rgba(255, 107, 0, 0.6) !important;
        transform: translateY(-1px) !important;
    }
</style>
"""


def apply_plotly_dark_theme(fig, title="", subtitle="", x_title="", y_title=""):
    """
    ปรับแต่ง Plotly Figure ให้เป็น Halloween Dark Theme
    ตัวหนังสือสีสว่าง (#F8FAFC, #CBD5E1) อ่านชัดบนพื้นหลังมืด
    ฟอนต์: 'Prompt', sans-serif
    """
    title_text = f"<b>{title}</b>"
    if subtitle:
        title_text += f"<br><span style='font-size:12px; color:#C084FC; font-weight:normal;'>{subtitle}</span>"

    fig.update_layout(
        title={
            "text": title_text,
            "x": 0.01,
            "xanchor": "left",
            "y": 0.96,
            "font": {"family": FONT_FAMILY, "size": 15, "color": "#FFFFFF"}
        },
        font={"family": FONT_FAMILY, "size": 12, "color": "#F1F5F9"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(14, 14, 24, 0.65)",
        margin={"l": 40, "r": 30, "t": 75 if subtitle else 55, "b": 45},
        hoverlabel={
            "bgcolor": "#121220",
            "font_size": 12,
            "font_family": FONT_FAMILY,
            "bordercolor": "#8A2BE2",
            "font_color": "#FFFFFF"
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11, "color": "#F1F5F9"}
        }
    )

    if x_title:
        fig.update_xaxes(
            title_text=x_title,
            title_font={"size": 12, "color": "#E2E8F0"},
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            zeroline=False,
            tickfont={"size": 11, "color": "#F1F5F9"}
        )
    else:
        fig.update_xaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)", zeroline=False, tickfont={"color": "#F1F5F9"})

    if y_title:
        fig.update_yaxes(
            title_text=y_title,
            title_font={"size": 12, "color": "#E2E8F0"},
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            zeroline=False,
            tickfont={"size": 11, "color": "#F1F5F9"}
        )
    else:
        fig.update_yaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)", zeroline=False, tickfont={"color": "#F1F5F9"})

    return fig
