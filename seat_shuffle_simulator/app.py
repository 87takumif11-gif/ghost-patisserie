import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Alignment, Border, Side, Font
from io import BytesIO
import random

# =====================================================================
# 1. PAGE CONFIGURATION & STATE INITIALIZATION
# =====================================================================
st.set_page_config(
    page_title="自動席替えシミュレーター",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State variables for 7x7 grid
if "active_seats" not in st.session_state:
    # By default, all 7x7 seats (49 seats) are active
    st.session_state.active_seats = {(c, r) for c in range(7) for r in range(7)}
if "fixed_seats" not in st.session_state:
    st.session_state.fixed_seats = {}  # key: (col, row), value: student_id
if "assigned_seats" not in st.session_state:
    st.session_state.assigned_seats = {}  # key: (col, row), value: student_id
if "selected_seat" not in st.session_state:
    st.session_state.selected_seat = None  # (col, row) tuple
if "start_num" not in st.session_state:
    st.session_state.start_num = 1
if "end_num" not in st.session_state:
    st.session_state.end_num = 36
if "absent_nums" not in st.session_state:
    st.session_state.absent_nums = ""
if "operation_mode" not in st.session_state:
    st.session_state.operation_mode = "座席の設置・解除 (レイアウト作成)"

# =====================================================================
# 2. SEAT SELECTION INTERACTION (HANDLED NATIVELY VIA CALLBACKS)
# =====================================================================

# =====================================================================
# 3. PREMIUM UI STYLE INJECTION
# =====================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Noto+Sans+JP:wght@300;400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', 'Noto Sans JP', sans-serif;
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color) !important;
    }
    
    .app-header {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .app-header h1 {
        color: white !important;
        margin: 0 0 10px 0 !important;
        font-weight: 800;
        font-size: 2.2rem;
    }
    .app-header p {
        margin: 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    .blackboard-container {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
    }
    .blackboard {
        width: 80%;
        max-width: 600px;
        background: linear-gradient(135deg, #14532d, #064e3b);
        color: #e2e8f0;
        text-align: center;
        padding: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 0.3em;
        border-radius: 8px;
        border: 4px solid #78350f;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .classroom-container {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 30px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
    }
    
    @media (prefers-color-scheme: dark) {
        .classroom-container {
            background-color: #1e293b;
            border-color: #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }
    }
    
    .grid-layout {
        display: flex;
        justify-content: center;
        gap: 15px;
        overflow-x: auto;
        padding: 10px 0;
    }
    
    .grid-column {
        display: flex;
        flex-direction: column;
        gap: 12px;
        align-items: center;
    }
    
    .grid-column-header {
        text-align: center;
        font-weight: 700;
        color: #4b5563;
        font-size: 0.85rem;
        margin-bottom: 12px;
        background-color: #f3f4f6;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-block;
        width: 100%;
    }
    
    @media (prefers-color-scheme: dark) {
        .grid-column-header {
            color: #cbd5e1;
            background-color: #1e293b;
        }
    }
    
    .metric-card {
        background-color: #ffffff;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        color: #1e293b;
    }
    
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background-color: #1e293b;
            border-color: #334155;
            color: #f8fafc;
        }
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
    }
    
    @media (prefers-color-scheme: dark) {
        .metric-label {
            color: #94a3b8;
        }
    }
    
    .metric-val-blue {
        color: #1e3a8a;
    }
    .metric-val-green {
        color: #10b981;
    }
    .metric-val-accent {
        color: #3b82f6;
    }
    
    @media (prefers-color-scheme: dark) {
        .metric-val-blue {
            color: #60a5fa !important;
        }
        .metric-val-green {
            color: #34d399 !important;
        }
        .metric-val-accent {
            color: #60a5fa !important;
        }
    }
    
    .selected-seat-inspector {
        background: linear-gradient(135deg, #fef3c7, #fffbeb);
        border: 1px solid #fde68a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: #92400e;
    }
    
    @media (prefers-color-scheme: dark) {
        .selected-seat-inspector {
            background: linear-gradient(135deg, #78350f, #451a03);
            border-color: #b45309;
            color: #fef3c7;
        }
    }
    
    /* Native Streamlit Seat Button Styles */
    div[data-testid="stHorizontalBlock"] button {
        height: 78px !important;
        border-radius: 12px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        padding: 6px !important;
        font-family: 'Outfit', 'Noto Sans JP', sans-serif !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        white-space: pre-line !important;
        border: none !important;
    }
    
    /* 1. Inactive seats (Aisles) */
    button.seat-inactive-btn {
        background-color: #f1f5f9 !important;
        color: #94a3b8 !important;
        border: 1px dotted #cbd5e1 !important;
        box-shadow: none !important;
    }
    button.seat-inactive-btn:hover {
        background-color: #e2e8f0 !important;
        border-color: #94a3b8 !important;
    }
    
    @media (prefers-color-scheme: dark) {
        button.seat-inactive-btn {
            background-color: #0f172a !important; /* slate-900 */
            color: #475569 !important; /* slate-600 */
            border: 1px dotted #334155 !important; /* slate-700 */
        }
        button.seat-inactive-btn:hover {
            background-color: #1e293b !important;
            border-color: #475569 !important;
        }
    }
    
    /* 2. Fixed seats (Deep forest green) */
    button.seat-fixed-btn {
        background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(27, 94, 32, 0.2) !important;
        font-weight: bold !important;
    }
    button.seat-fixed-btn:hover {
        box-shadow: 0 6px 16px rgba(27, 94, 32, 0.35) !important;
        transform: translateY(-2px) !important;
    }
    
    @media (prefers-color-scheme: dark) {
        button.seat-fixed-btn {
            background: linear-gradient(135deg, #064e3b, #047857) !important;
            box-shadow: 0 4px 12px rgba(6, 78, 59, 0.4) !important;
        }
        button.seat-fixed-btn:hover {
            box-shadow: 0 6px 16px rgba(4, 120, 87, 0.5) !important;
        }
    }
    
    /* 3. Assigned seats (Medium emerald green) */
    button.seat-assigned-btn {
        background: linear-gradient(135deg, #34d399, #10b981) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
        font-weight: bold !important;
    }
    button.seat-assigned-btn:hover {
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35) !important;
        transform: translateY(-2px) !important;
    }
    
    @media (prefers-color-scheme: dark) {
        button.seat-assigned-btn {
            background: linear-gradient(135deg, #059669, #10b981) !important;
            box-shadow: 0 4px 12px rgba(5, 150, 105, 0.4) !important;
        }
        button.seat-assigned-btn:hover {
            box-shadow: 0 6px 16px rgba(16, 185, 129, 0.5) !important;
        }
    }
    
    /* 4. Selected seats (Gold border) */
    button.seat-selected-btn {
        background-color: #fffbeb !important;
        color: #b45309 !important;
        border: 3.5px solid #fbbf24 !important;
        box-shadow: 0 0 15px rgba(251, 191, 36, 0.5) !important;
        transform: scale(1.05) !important;
        font-weight: bold !important;
    }
    button.seat-selected-btn:hover {
        background-color: #fef3c7 !important;
    }
    
    @media (prefers-color-scheme: dark) {
        button.seat-selected-btn {
            background-color: #78350f !important;
            color: #fef3c7 !important;
            border: 3.5px solid #fbbf24 !important;
            box-shadow: 0 0 15px rgba(251, 191, 36, 0.6) !important;
        }
        button.seat-selected-btn:hover {
            background-color: #92400e !important;
        }
    }
    
    /* 5. Active empty seats (Light mint green with dashed green border) */
    button.seat-empty-btn {
        background: #e8f5e9 !important;
        border: 2px dashed #81c784 !important;
        color: #2e7d32 !important;
        box-shadow: none !important;
        font-weight: 600 !important;
    }
    button.seat-empty-btn:hover {
        background: #c8e6c9 !important;
        border-color: #4caf50 !important;
        transform: translateY(-2px) !important;
    }
    
    @media (prefers-color-scheme: dark) {
        button.seat-empty-btn {
            background: #064e3b !important; /* emerald-900 */
            border: 2px dashed #059669 !important; /* emerald-600 */
            color: #a7f3d0 !important; /* emerald-200 */
        }
        button.seat-empty-btn:hover {
            background: #047857 !important; /* emerald-800 */
            border-color: #10b981 !important; /* emerald-500 */
        }
    }
    
    /* Printing Overrides for class-based buttons */
    @media print {
        header, [data-testid="stSidebar"], .no-print, [data-testid="stHeader"] {
            display: none !important;
        }
        body, [data-testid="stAppViewContainer"] {
            background-color: white !important;
        }
        .classroom-container {
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        button.seat-inactive-btn {
            visibility: hidden !important;
            border: none !important;
            background: none !important;
            box-shadow: none !important;
        }
        button.seat-empty-btn, button.seat-selected-btn {
            border: 1px solid #cbd5e1 !important;
            background: white !important;
            color: black !important;
            box-shadow: none !important;
        }
        button.seat-fixed-btn {
            border: 2px solid #1b5e20 !important;
            background: white !important;
            color: black !important;
            box-shadow: none !important;
        }
        button.seat-assigned-btn {
            border: 1px solid #10b981 !important;
            background: white !important;
            color: black !important;
            box-shadow: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# 3.5 JAVASCRIPT HYBRID CLASS-TOGGLE FOR SEAT BUTTONS
# =====================================================================
# Injects JS that runs locally and periodically sets class names on buttons
# matching specific text contents (e.g. × 通路, [固定], etc.) so CSS handles styling.
js_code = """
<script>
const updateButtonClasses = () => {
    let doc = document;
    try {
        if (window.parent && window.parent.document) {
            doc = window.parent.document;
        }
    } catch(e) {
        doc = document;
    }
    
    const buttons = doc.querySelectorAll('button');
    buttons.forEach(btn => {
        const text = btn.innerText || '';
        
        // Skip non-seat buttons
        if (!text.includes('× 通路') && !text.includes('席 ') && !text.includes('🔒') && !text.includes('👤')) {
            return;
        }
        
        // Remove old styling classes
        btn.classList.remove('seat-inactive-btn', 'seat-fixed-btn', 'seat-assigned-btn', 'seat-selected-btn', 'seat-empty-btn');
        
        // Match text and apply corresponding classes
        if (text.includes('× 通路')) {
            btn.classList.add('seat-inactive-btn');
        } else if (text.includes('[選択中]')) {
            btn.classList.add('seat-selected-btn');
        } else if (text.includes('[固定]')) {
            btn.classList.add('seat-fixed-btn');
        } else if (text.includes('[設置済]')) {
            btn.classList.add('seat-assigned-btn');
        } else if (text.includes('[解除]')) {
            btn.classList.add('seat-empty-btn');
        }
    });
};

// Polling interval of 100ms
setInterval(updateButtonClasses, 100);
</script>
"""
st.components.v1.html(js_code, height=0, width=0)


# =====================================================================
# 4. APP HEADER
# =====================================================================
st.markdown('<div class="app-header"><h1>🏫 自動席替えシミュレーター</h1><p>7×7（計49席）のグリッドから、使用する席を直接クリックして設置・解除できます。特定座席の固定、ランダム席替え、Excel出力を個人情報（生徒名）を一切使わずに行えます。</p></div>', unsafe_allow_html=True)

# =====================================================================
# 5. SIDEBAR CONFIGURATIONS & DYNAMIC STUDENT POOL CALCULATION
# =====================================================================
st.sidebar.markdown("### ⚙️ 各種設定・操作")

# --- EXPANDER 1: Student Settings ---
with st.sidebar.expander("👤 生徒データ設定", expanded=True):
    start_num = st.number_input(
        "開始出席番号",
        min_value=1,
        max_value=150,
        value=st.session_state.start_num,
        step=1,
        key="start_num_input"
    )
    if start_num != st.session_state.start_num:
        st.session_state.start_num = start_num
        st.rerun()
        
    end_num = st.number_input(
        "終了出席番号",
        min_value=start_num,
        max_value=200,
        value=max(st.session_state.end_num, start_num),
        step=1,
        key="end_num_input"
    )
    if end_num != st.session_state.end_num:
        st.session_state.end_num = end_num
        st.rerun()
        
    absent_nums_str = st.text_input(
        "欠番 (カンマ区切り)",
        value=st.session_state.absent_nums,
        placeholder="例: 4, 12, 25",
        help="欠席やクラスに存在しない出席番号をカンマ区切りで入力します。"
    )
    if absent_nums_str != st.session_state.absent_nums:
        st.session_state.absent_nums = absent_nums_str
        st.rerun()

# Parse absent list
absent_list = []
if st.session_state.absent_nums.strip():
    for x in st.session_state.absent_nums.replace('\n', ',').split(','):
        x_str = x.strip()
        if x_str.isdigit():
            absent_list.append(int(x_str))

# Calculate student pool
students_pool = []
for x in range(st.session_state.start_num, st.session_state.end_num + 1):
    if x not in absent_list:
        students_pool.append(str(x))

student_count = len(students_pool)

# Display student summary in sidebar
st.sidebar.markdown(f"**現在の生徒総数:** `{student_count}人` (欠番を除く)")
if students_pool:
    disp_str = ", ".join(students_pool)
    if len(disp_str) > 50:
        disp_str = disp_str[:50] + "..."
    st.sidebar.caption(f"対象番号: {disp_str}")

# --- EXPANDER 2: Active Seat Settings ---
st.sidebar.markdown("### 🪑 固定席の設定")
if st.session_state.operation_mode == "固定席の設定 (特定生徒の配置)":
    if st.session_state.selected_seat:
        sc, sr = st.session_state.selected_seat
        
        # Ensure selected seat is active and within bounds
        if sc < 7 and sr < 7 and (sc, sr) in st.session_state.active_seats:
            is_fixed = (sc, sr) in st.session_state.fixed_seats
            current_student = st.session_state.fixed_seats.get((sc, sr), "")
            
            st.sidebar.markdown(
                f"""
                <div class="selected-seat-inspector">
                    <strong>📍 選択位置:</strong> {sc+1}列目 - {sr+1}行目<br>
                    <span>生徒を固定する席を選択し、設定してください。</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            fix_toggle = st.sidebar.checkbox(
                "この座席を固定する (ホールド)",
                value=is_fixed,
                key=f"sidebar_fix_toggle_{sc}_{sr}"
            )
            
            if fix_toggle:
                student_options = [""] + students_pool
                default_idx = 0
                if str(current_student) in student_options:
                    default_idx = student_options.index(str(current_student))
                    
                selected_student = st.sidebar.selectbox(
                    "配置する生徒を選択",
                    options=student_options,
                    index=default_idx,
                    key=f"sidebar_student_select_{sc}_{sr}",
                    help="あらかじめこの座席に固定したい出席番号を選択します。"
                )
                
                if selected_student:
                    # Check if student is fixed elsewhere
                    already_fixed_elsewhere = [coord for coord, val in st.session_state.fixed_seats.items() if val == selected_student and coord != (sc, sr)]
                    if already_fixed_elsewhere:
                        other_c, other_r = already_fixed_elsewhere[0]
                        st.sidebar.warning(f"⚠️ 生徒 #{selected_student} は既に {other_c+1}列目-{other_r+1}行目の席に固定されています。この席に割り当てると、前の固定は解除されます。")
                        
                    st.session_state.fixed_seats[(sc, sr)] = selected_student
                    for coord in already_fixed_elsewhere:
                        st.session_state.fixed_seats.pop(coord, None)
                        st.session_state.assigned_seats.pop(coord, None)
                        
                    st.session_state.assigned_seats[(sc, sr)] = selected_student
                else:
                    st.session_state.fixed_seats.pop((sc, sr), None)
                    st.session_state.assigned_seats.pop((sc, sr), None)
            else:
                st.session_state.fixed_seats.pop((sc, sr), None)
                st.session_state.assigned_seats.pop((sc, sr), None)
                
            if st.sidebar.button("選択を解除する", use_container_width=True):
                st.session_state.selected_seat = None
                st.rerun()
        else:
            st.session_state.selected_seat = None
            st.sidebar.info("グリッド上の有効な座席をクリックすると、ここに固定席設定が表示されます。")
    else:
        st.sidebar.info("グリッド上の有効な座席をクリックすると、ここに固定席設定が表示されます。")
else:
    st.sidebar.info("💡 レイアウト作成モードになっています。上の操作モードで「固定席の設定」に切り替えてから座席をクリックしてください。")

# =====================================================================
# 6. MAIN CONTENT LAYOUT
# =====================================================================

# --- SECTION 6a: Metrics Cards ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">🪑 設置された座席数</span><br>
            <span style="font-size:1.8rem;font-weight:800;" class="metric-val-blue">{len(st.session_state.active_seats)}</span> 席 / 49席
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">👤 生徒総数</span><br>
            <span style="font-size:1.8rem;font-weight:800;" class="metric-val-blue">{student_count}</span> 人
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">🔒 固定席数</span><br>
            <span style="font-size:1.8rem;font-weight:800;" class="metric-val-green">{len(st.session_state.fixed_seats)}</span> 席
        </div>
        """,
        unsafe_allow_html=True
    )
with col4:
    remaining_spots = len(st.session_state.active_seats) - len(st.session_state.fixed_seats)
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">🔄 シャッフル対象席</span><br>
            <span style="font-size:1.8rem;font-weight:800;" class="metric-val-accent">{remaining_spots}</span> 席
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# --- SECTION 6b: Classroom Seat Grid Rendering & Mode Selection ---
st.markdown("### 🛠️ 教室レイアウト編集・固定席設定")

mode_option = st.radio(
    "👉 グリッドのクリック操作モード：",
    options=["座席の設置・解除 (レイアウト作成)", "固定席の設定 (特定生徒の配置)"],
    index=0 if st.session_state.operation_mode == "座席の設置・解除 (レイアウト作成)" else 1,
    key="operation_mode_radio",
    horizontal=True,
    help="「レイアウト作成」モードでは、グリッドの席をクリックするだけで設置/解除ができます。「固定席の設定」モードでは、席をクリックして特定の生徒を固定できます。"
)

# Synchronize back to session state
if mode_option != st.session_state.operation_mode:
    st.session_state.operation_mode = mode_option
    st.session_state.selected_seat = None  # Reset selection when mode changes
    st.rerun()

# Layout Helper Buttons (Quick Actions)
if st.session_state.operation_mode == "座席の設置・解除 (レイアウト作成)":
    hcol1, hcol2, _ = st.columns([1.5, 1.5, 5])
    with hcol1:
        if st.button("🧼 すべての席を有効にする", use_container_width=True):
            st.session_state.active_seats = {(c, r) for c in range(7) for r in range(7)}
            st.session_state.selected_seat = None
            st.rerun()
    with hcol2:
        if st.button("❌ すべての席を解除（通路）にする", use_container_width=True):
            st.session_state.active_seats = set()
            st.session_state.fixed_seats = {}
            st.session_state.assigned_seats = {}
            st.session_state.selected_seat = None
            st.rerun()
            
st.write("")
st.markdown('<div class="blackboard-container"><div class="blackboard">ーーー 黒板 / 教卓 ーーー</div></div>', unsafe_allow_html=True)

# Render 7x7 Grid using native Streamlit columns and buttons
grid_cols = st.columns(7)
for c in range(7):
    with grid_cols[c]:
        st.markdown(f"<div class='grid-column-header'>{c+1}列目</div>", unsafe_allow_html=True)
        
        for r in range(7):
            seat_coord = (c, r)
            is_active = seat_coord in st.session_state.active_seats
            is_fixed = seat_coord in st.session_state.fixed_seats
            is_selected = seat_coord == st.session_state.selected_seat
            
            # Determine button labels
            if not is_active:
                label = "× 通路\n[設置]"
            else:
                if is_fixed:
                    label = f"🔒 #{st.session_state.fixed_seats[seat_coord]}\n[固定]"
                elif seat_coord in st.session_state.assigned_seats:
                    label = f"👤 #{st.session_state.assigned_seats[seat_coord]}\n[設置済]"
                else:
                    if is_selected:
                        label = f"席 {c+1}-{r+1}\n[選択中]"
                    else:
                        label = f"席 {c+1}-{r+1}\n[解除]"
            
            # Render button and handle click callback directly
            if st.button(label, key=f"seat_btn_{c}_{r}", use_container_width=True):
                mode = st.session_state.operation_mode
                if mode == "座席の設置・解除 (レイアウト作成)":
                    if is_active:
                        st.session_state.active_seats.discard(seat_coord)
                        st.session_state.fixed_seats.pop(seat_coord, None)
                        st.session_state.assigned_seats.pop(seat_coord, None)
                    else:
                        st.session_state.active_seats.add(seat_coord)
                    st.session_state.selected_seat = None
                else:
                    # Fixed seat mode
                    if is_active:
                        st.session_state.selected_seat = seat_coord
                    else:
                        st.session_state.selected_seat = None
                st.rerun()

st.caption("💡 操作モードが「レイアウト作成」の時は、席をクリックするだけで有効（机）と無効（通路）が即時切り替わります。必要な人数分の座席が設置されているかご確認ください。")

# =====================================================================
# 7. OPERATION ACTIONS (SHUFFLE, EXPORT)
# =====================================================================
st.markdown("### 🛠️ 席替えの実行と出力")

act_col1, act_col2 = st.columns([1, 1])

with act_col1:
    if st.button("🔄 席替えを実行する", type="primary", use_container_width=True):
        # Validation checks
        if student_count > len(st.session_state.active_seats):
            st.error(f"⚠️ 生徒人数 ({student_count}人) が設置された座席数 ({len(st.session_state.active_seats)}席) を超えています。")
        else:
            invalid_fixed = [val for coord, val in st.session_state.fixed_seats.items() if val not in students_pool or coord not in st.session_state.active_seats]
            if invalid_fixed:
                st.error("⚠️ 固定席の設定に問題があります（有効になっていない席、または現在の生徒リスト/出席番号の範囲に含まれない値が含まれています）。")
            else:
                # Filter student pool to exclude fixed ones
                fixed_students = {val for coord, val in st.session_state.fixed_seats.items() if coord in st.session_state.active_seats}
                remaining_students = [s for s in students_pool if s not in fixed_students]
                
                # Filter active empty seats
                empty_seats = [coord for coord in st.session_state.active_seats if coord not in st.session_state.fixed_seats]
                
                # Shuffle remaining students
                random.shuffle(remaining_students)
                
                # Synchronize and keep only active fixed seats
                st.session_state.assigned_seats = {coord: val for coord, val in st.session_state.fixed_seats.items() if coord in st.session_state.active_seats}
                
                # Assign shuffled students
                num_to_assign = min(len(remaining_students), len(empty_seats))
                for i in range(num_to_assign):
                    seat = empty_seats[i]
                    st.session_state.assigned_seats[seat] = remaining_students[i]
                    
                # Warn if leftover
                leftovers = remaining_students[num_to_assign:]
                if leftovers:
                    st.warning(f"⚠️ 座席数が足りないため、以下の生徒が配置できませんでした: {', '.join(leftovers)}")
                    
                st.success("🎉 席替えが正常に実行されました！")
                st.rerun()

with act_col2:
    exp_col1, exp_col2 = st.columns([1, 1])
    
    with exp_col1:
        if st.session_state.assigned_seats:
            def get_excel_buffer():
                wb = openpyxl.Workbook()
                
                # --- Font and Fill Definitions ---
                font_title = Font(name="Meiryo", size=16, bold=True, color="1e3a8a")
                font_board = Font(name="Meiryo", size=11, bold=True, color="FFFFFF")
                font_header = Font(name="Meiryo", size=10, bold=True, color="475569")
                font_seat_num = Font(name="Meiryo", size=12, bold=True)
                
                fill_board = PatternFill(start_color="14532d", end_color="14532d", fill_type="solid")
                fill_fixed = PatternFill(start_color="d1fae5", end_color="d1fae5", fill_type="solid")
                fill_assigned = PatternFill(start_color="dbeafe", end_color="dbeafe", fill_type="solid")
                fill_empty = PatternFill(start_color="f9fafb", end_color="f9fafb", fill_type="solid")
                fill_inactive = PatternFill(start_color="e2e8f0", end_color="e2e8f0", fill_type="solid")
                
                border_thin = Border(
                    left=Side(style='thin', color='cbd5e1'),
                    right=Side(style='thin', color='cbd5e1'),
                    top=Side(style='thin', color='cbd5e1'),
                    bottom=Side(style='thin', color='cbd5e1')
                )
                
                # --- SHEET 1: Normal (教卓が上 / 先生視点) ---
                ws1 = wb.active
                ws1.title = "教卓が上 (先生視点)"
                ws1.views.sheetView[0].showGridLines = True
                
                ws1.merge_cells(start_row=2, start_column=2, end_row=2, end_column=8)
                title_cell1 = ws1.cell(row=2, column=2, value="教室座席表 (教卓が上・先生視点)")
                title_cell1.font = font_title
                title_cell1.alignment = Alignment(horizontal="center", vertical="center")
                ws1.row_dimensions[2].height = 40
                
                ws1.merge_cells(start_row=4, start_column=2, end_row=4, end_column=8)
                board_cell1 = ws1.cell(row=4, column=2, value="ーーー 黒板 / 教卓 ーーー")
                board_cell1.font = font_board
                board_cell1.fill = fill_board
                board_cell1.alignment = Alignment(horizontal="center", vertical="center")
                ws1.row_dimensions[4].height = 28
                
                for col_idx in range(7):
                    cell = ws1.cell(row=6, column=col_idx+2, value=f"{col_idx+1}列目")
                    cell.font = font_header
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    ws1.column_dimensions[openpyxl.utils.get_column_letter(col_idx+2)].width = 15
                ws1.row_dimensions[6].height = 20
                
                for r_idx in range(7):
                    excel_row = 8 + r_idx
                    ws1.row_dimensions[excel_row].height = 30
                    
                    for c_idx in range(7):
                        coord = (c_idx, r_idx)
                        is_active = coord in st.session_state.active_seats
                        is_fixed = coord in st.session_state.fixed_seats
                        
                        if not is_active:
                            student_val = ""
                            fill = fill_inactive
                        else:
                            if is_fixed:
                                student_val = st.session_state.fixed_seats[coord]
                                fill = fill_fixed
                            elif coord in st.session_state.assigned_seats:
                                student_val = st.session_state.assigned_seats[coord]
                                fill = fill_assigned
                            else:
                                student_val = ""
                                fill = fill_empty
                                
                        if isinstance(student_val, str) and student_val.isdigit():
                            write_val = int(student_val)
                        else:
                            write_val = student_val
                            
                        cell = ws1.cell(row=excel_row, column=c_idx+2, value=write_val)
                        cell.font = font_seat_num
                        cell.fill = fill
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                        if is_active:
                            cell.border = border_thin

                # --- SHEET 2: Rotated 180 (教卓が下 / 生徒視点) ---
                ws2 = wb.create_sheet(title="教卓が下 (生徒視点)")
                ws2.views.sheetView[0].showGridLines = True
                
                ws2.merge_cells(start_row=2, start_column=2, end_row=2, end_column=8)
                title_cell2 = ws2.cell(row=2, column=2, value="教室座席表 (教卓が下・生徒視点・180度回転)")
                title_cell2.font = font_title
                title_cell2.alignment = Alignment(horizontal="center", vertical="center")
                ws2.row_dimensions[2].height = 40
                
                for r_idx in range(7):
                    excel_row = 4 + (6 - r_idx)  # r_idx=0 (front row) -> row 10, r_idx=6 (back row) -> row 4
                    ws2.row_dimensions[excel_row].height = 30
                    
                    for c_idx in range(7):
                        excel_col = 2 + (6 - c_idx)  # c_idx=0 (1st col) -> col 8, c_idx=6 (7th col) -> col 2
                        coord = (c_idx, r_idx)
                        is_active = coord in st.session_state.active_seats
                        is_fixed = coord in st.session_state.fixed_seats
                        
                        if not is_active:
                            student_val = ""
                            fill = fill_inactive
                        else:
                            if is_fixed:
                                student_val = st.session_state.fixed_seats[coord]
                                fill = fill_fixed
                            elif coord in st.session_state.assigned_seats:
                                student_val = st.session_state.assigned_seats[coord]
                                fill = fill_assigned
                            else:
                                student_val = ""
                                fill = fill_empty
                                
                        if isinstance(student_val, str) and student_val.isdigit():
                            write_val = int(student_val)
                        else:
                            write_val = student_val
                            
                        cell = ws2.cell(row=excel_row, column=excel_col, value=write_val)
                        cell.font = font_seat_num
                        cell.fill = fill
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                        if is_active:
                            cell.border = border_thin
                            
                for col_idx in range(7):
                    excel_col = 2 + (6 - col_idx)  # col_idx=0 (1st col) -> col 8, col_idx=6 (7th col) -> col 2
                    cell = ws2.cell(row=11, column=excel_col, value=f"{col_idx+1}列目")
                    cell.font = font_header
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    ws2.column_dimensions[openpyxl.utils.get_column_letter(excel_col)].width = 15
                ws2.row_dimensions[11].height = 20
                
                ws2.merge_cells(start_row=13, start_column=2, end_row=13, end_column=8)
                board_cell2 = ws2.cell(row=13, column=2, value="ーーー 黒板 / 教卓 ーーー")
                board_cell2.font = font_board
                board_cell2.fill = fill_board
                board_cell2.alignment = Alignment(horizontal="center", vertical="center")
                ws2.row_dimensions[13].height = 28
                
                buffer = BytesIO()
                wb.save(buffer)
                buffer.seek(0)
                return buffer
                
            excel_data = get_excel_buffer()
            st.download_button(
                label="📥 結果をExcelでダウンロードする",
                data=excel_data,
                file_name="seating_chart_7x7.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="「教卓が上（先生視点）」と「教卓が下（生徒視点・180度回転）」の2つのシートが含まれたExcelファイルを出力します。"
            )
        else:
            st.button("📥 結果をExcelでダウンロードする (席替え未実行)", disabled=True, use_container_width=True)
            
    with exp_col2:
        show_print = st.checkbox("🖥️ 印刷用表示", key="show_print_view")
        if show_print:
            st.info("💡 印刷用表示モード。Cmd+P / Ctrl+PでA4横向き印刷できます。")

# =====================================================================
# 8. GENERAL INSTRUCTIONS & CREDITS
# =====================================================================
st.markdown("---")
with st.expander("ℹ️ アプリの使い方ガイド"):
    st.markdown(
        """
        1. **生徒の設定（出席番号の入力）**
           - 左側サイドバーの「生徒データ設定」で開始番号（例：1）と終了番号（例：36）を設定します。
           - 不在の番号（欠番）があれば「欠番 (カンマ区切り)」に入力します（例: `4, 12`）。
           - これらをもとに生徒の総数が自動計算されます。
        2. **座席レイアウトの作成**
           - 「操作モード」を「座席の設置・解除 (レイアウト作成)」にします。
           - 7×7のグリッド上の席を直接クリックしていくことで、席の設置と解除（通路化）が瞬時に行えます。
           - 「すべての席を無効（通路）にする」ボタンを押し、配置したい場所だけクリックしていく方法も大変便利です。
        3. **固定席の指定**
           - 「操作モード」を「固定席の設定 (特定生徒の配置)」に切り替えます。
           - 生徒を固定したい席（例: 最前列など）をクリックし、左側サイドバーに表示される「配置する生徒を選択」から出席番号を指定します。固定された席は緑色になり、🔒マークが表示されます。
        4. **席替えの実行**
           - 「席替えを実行する」ボタンを押すと、固定席以外の生徒が有効な座席にランダムシャッフルされます。
        5. **印刷と出力**
           - 「結果をExcelでダウンロードする」をクリックすると、通路部分が灰色背景で表現された、美しいExcelファイルが出力されます（ファイルには「教卓が上」と「教卓が下（180度回転）」の2つのシートが含まれています）。
           - 「印刷用表示」をチェックすると、不要なメニューが非表示になり、ブラウザの印刷機能（A4横向き推奨）からきれいに印刷できます（印刷時、通路は非表示になります）。
        """
    )

st.markdown('<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 30px; margin-bottom: 15px;">© 2026 自動席替えシミュレーター | 個人情報保護のためブラウザ内完結設計</div>', unsafe_allow_html=True)
