import streamlit as st
import pandas as pd
import numpy as np

# --- 頁面設定 ---
st.set_page_config(page_title="小學概覽選校搜尋器", layout="wide")

# --- 注入 CSS 實現 Tab 滾動提示、表格樣式、側邊欄按鈕優化及顏色背景設定 ---
st.markdown("""
    <style>
    /* [NEW] 顏色背景設定 */
    .stApp {
        /* 使用全白色背景 */
        background-color: #FFFFFF; 
        
        /* 移除圖片相關設定 */
        background-image: none; 
        background-size: auto; 
        background-position: initial; 
        background-attachment: initial; 
        background-repeat: initial; 
    }

    /* [NEW] 側邊欄調整透明度，使其更貼合白色背景 */
    [data-testid="stSidebar"] {
        /* 設置為近乎不透明的白色，確保內容清晰可讀 */
        background-color: rgba(255, 255, 255, 0.95); 
    }

    /* 確保 Logo 和標題在同一行並垂直居中 */
    .header-container {
        display: flex;
        align-items: center;
        gap: 15px; /* Logo 和標題之間的間距 */
        margin-bottom: 0rem;
    }
    .header-title {
        font-size: 2.25rem; /* 模擬 st.title 的大小 */
        font-weight: 700;
        margin: 0;
        padding-top: 5px; /* 輕微調整以與 Logo 更好地對齊 */
    }
    .header-logo {
        height: 50px; /* 控制 Logo 的大小 */
        width: auto;
    }

    /* 1. 基本容器設置 */
    div[data-testid="stTabs"] {
        position: relative;
        overflow-x: auto; /* 確保內容可以滾動 */
        padding-bottom: 5px; /* 留出空間 */
        /* 隱藏預設滾動條 */
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
    /* 隱藏 Chrome/Safari 滾動條 */
    div[data-testid="stTabs"] > div:first-child::-webkit-scrollbar {
        display: none;
    }

    /* 2. 移除所有箭頭/陰影提示 */
    div[data-testid="stTabs"]::after, div[data-testid="stTabs"]::before {
        content: none; 
        display: none;
    }
    
    /* 3. HTML 表格基本樣式 (通用於所有clean-table，解決響應式對齊問題) */
    .clean-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1em;
        table-layout: auto; 
        min-width: 400px; /* 確保在手機上仍有最小寬度以保持對齊 */
    }
    .clean-table th, .clean-table td {
        padding: 8px 12px;
        text-align: left;
        border: none; 
        border-bottom: 1px solid #eee; /* 增加行分隔線 */
        vertical-align: top;
    }
    .clean-table th {
        font-weight: 600;
        background-color: #f7f7f7;
        border-bottom: 2px solid #ccc; /* 標題下雙分隔線 */
    }
    
    /* 4. 測驗次數/班級結構 表格樣式優化 */
    .clean-table.class-table td:nth-child(n+2), .clean-table.class-table th:nth-child(n+2) {
        text-align: center;
    }
    .clean-table.class-table td:nth-child(1), .clean-table.assessment-table td:nth-child(1) {
        font-weight: bold; /* 讓第一欄文字粗體顯示 */
        width: 30%; 
    }
    
    /* 5. 政策列表樣式 - 單欄堆疊，確保內容清晰 */
    .policy-list-item {
        padding: 8px 0px;
        border-bottom: 1px solid #eee;
    }
    .policy-list-item:last-child {
        border-bottom: none;
    }
    .policy-list-item strong {
        display: block; 
        margin-bottom: 2px;
        color: #333;
    }

    /* 6. 側邊欄展開/摺疊按鈕優化 */
    /* 針對側邊欄展開按鈕 (通常在左上角) */
    button[data-testid="baseButton-headerNoPadding"] {
        color: #1abc9c !important; /* 強制設定為綠色 */
        font-size: 1.5rem; /* 增大圖標尺寸 */
        opacity: 1 !important; /* 確保它不會淡化 */
        transition: color 0.2s;
    }
    
    /* 針對側邊欄摺疊按鈕 (在側邊欄內部) */
    button[data-testid="stSidebarCloseButton"] {
        color: #e74c3c !important; /* 設為紅色，更醒目 */
        font-size: 1.5rem; /* 增大圖標尺寸 */
        opacity: 1 !important;
        transition: color 0.2s;
    }
    
    /* 鼠標懸停效果 */
    button[data-testid="baseButton-headerNoPadding"]:hover,
    button[data-testid="stSidebarCloseButton"]:hover {
        color: #3498db !important; /* 懸停時變為藍色 */
    }
    /* 新增：統一 info-table 樣式 */
    .info-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 15px;
    }
    .info-table th {
        background-color: #f7f7f7;
        font-weight: 600;
        border-bottom: 2px solid #ccc;
        padding: 8px 12px;
        text-align: left;
        width: 50%; /* 確保兩欄平均分配 */
    }
    .info-table td {
        padding: 6px 12px;
        border-bottom: 1px solid #eee;
        text-align: left;
        width: 50%;
    }
    .info-table td:nth-child(2) {
        text-align: right; /* 數字靠右顯示 */
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
# --- 注入 CSS 結束 ---

# --- Logo 及 主標題 ---

LOGO_URL = "https://raw.githubusercontent.com/kingyeung625/primary-school-selector/0147c6564ccd706049b1c3ed9885ecc920f70f9f/images.png"
TITLE_TEXT = "小學概覽選校搜尋器"

# 使用 st.markdown 和 HTML 結構將 Logo 和標題放在同一行
st.markdown(f"""
    <div class="header-container">
        <img class="header-logo" src="{LOGO_URL}" alt="App Logo">
        <h1 class="header-title">{TITLE_TEXT}</h1>
    </div>
    """, unsafe_allow_html=True)

# --- 初始化 Session State ---
if 'filtered_schools' not in st.session_state:
    st.session_state.filtered_schools = pd.DataFrame()

# 初始化篩選器按鈕狀態 (Filter buttons)
if 'master_filter' not in st.session_state:
    st.session_state.master_filter = 0
if 'exp_filter' not in st.session_state:
    st.session_state.exp_filter = 0
if 'sen_filter' not in st.session_state:
    st.session_state.sen_filter = 0

# --- 載入與處理資料 (簡化至純文字邏輯) ---
@st.cache_data
def load_data():
    try:
        # 使用您最新的檔案名稱
        school_df = pd.read_csv("database_school_info.csv") 
        article_df = pd.read_csv("database_related_article.csv")
        
        school_df.columns = school_df.columns.str.strip()
        article_df.columns = article_df.columns.str.strip()
        
        school_df.rename(columns={"學校類別1": "資助類型", "學校類別2": "上課時間"}, inplace=True)
        
        # 將所有列強制轉為字串並移除空格，以確保一致的純文字讀取
        for col in school_df.columns:
            school_df[col] = school_df[col].astype(str).str.strip()

        # 處理 HTML 換行符
        for col in school_df.select_dtypes(include=['object']).columns:
            school_df[col] = school_df[col].str.replace('<br>', '\n', regex=False).str.strip()
        
        if '學校名稱' in school_df.columns:
            school_df['學校名稱'] = school_df['學校名稱'].str.replace(r'\s+', ' ', regex=True).str.strip()
            
        return school_df, article_df
        
    except FileNotFoundError:
        st.error("錯誤：找不到資料檔案。請確保 'database_school_info.csv' 和 'database_related_article.csv' 檔案與 app.py 在同一個資料夾中。")
        return None, None
    except Exception as e:
        st.error(f"處理資料時發生錯誤：{e}。請檢查您的 CSV 檔案格式是否正確。")
        return None, None

# --- [START] 輔助函數 ---
# 這裡修改 LABEL_MAP (不變)
LABEL_MAP = { 
    "校監_校管會主席姓名": "校監", 
    "校長姓名": "校長",
    "舊生會_校友會": "舊生會／校友會", 
    "上課時間_": "一般上學時間",
    "放學時間": "一般放學時間",
    "午膳時間": "午膳開始時間",
    "午膳結束時間": "午膳結束時間",
    # 這些欄位將作為純文字顯示
    "核准編制教師職位數目": "核准編制教師職位數目", 
    "教師總人數": "教師總人數", 
    "已接受師資培訓人數百分率": "已接受師資培訓 (%)", # 在顯示名稱中保留百分比提示
    "學士人數百分率": "學士學位 (%)",
    "碩士／博士或以上人數百分率": "碩士/博士學位 (%)",
    "特殊教育培訓人數百分率": "特殊教育培訓 (%)",
    "0至4年年資人數百分率": "0-4年年資 (%)", 
    "5至9年年資人數百分率": "5-9年年資 (%)", 
    "10年年資或以上人數百分率": "10+年年資 (%)", 
    "課室數目": "課室",
    "禮堂數目": "禮堂",
    "操場數目": "操場",
    "圖書館數目": "圖書館",
    "學費": "學費",
    "堂費": "堂費",
    "家長教師會費": "家長教師會費",
    "非標準項目的核准收費": "非標準項目的核准收費",
    "其他收費_費用": "其他",
    "一條龍中學": "一條龍中學",
    "直屬中學": "直屬中學",
    "聯繫中學": "聯繫中學",
    "校訓": "校訓",
    # 新增/移動的欄位名稱
    "健康校園生活": "健康校園生活",
    "學校生活備註": "學校生活備註",
    "全方位學習": "全方位學習",
    "家校合作": "家校合作",
    "全校參與照顧學生的多樣性": "全校參與照顧學生的多樣性",
    "全校參與模式融合教育": "全校參與模式融合教育",
    "非華語學生的教育支援": "非華語學生的教育支援",
    "學費減免": "學費減免",
    "環保政策": "環保政策",
    "校風": "校風",
    "學校發展計劃": "學校發展計劃",
    "學校管理架構": "學校管理架構",
    "法團校董會_校管會_校董會": "法團校董會/校管會/校董會",
    "學校特色_其他": "其他學校特色",
    "課程剪裁及調適措施": "課程剪裁及調適措施",
    "正確價值觀_態度和行為的培養": "正確價值觀、態度和行為的培養",
    "共通能力的培養": "共通能力的培養",
    "小學教育課程更新重點的發展": "小學教育課程更新重點的發展",
    "學習和教學策略": "學習和教學策略",
    "學校關注事項": "學校關注事項",
}

def is_valid_data(value):
    # 🚨 修正：在進行任何字串操作前，強制將值轉換為字串。
    # 這可以避免 'float' object has no attribute 'strip' 錯誤，因為 numpy.nan 是 float 類型。
    value_str = str(value).strip() 
    
    # 檢查是否為非空字串，且不是字串 'nan' 或 '-'
    return bool(value_str) and value_str.lower() not in ['nan', '-']

# 僅顯示評估數字（現簡化為顯示純文字）
def display_assessment_count(value):
    # 由於 is_valid_data 已經確保 value 是一個清理過的字串
    if is_valid_data(value):
        return str(value)
    return "-"

# 格式化篩選器按鈕的高亮樣式 (保持不變)
def style_filter_button(label, value, filter_key):
    is_selected = st.session_state[filter_key] == value
    style = """
        <style>
        /* This ensures the CSS is applied to all buttons in the section */
        div.stButton > button {
            background-color: transparent;
            color: #1abc9c;
            border-radius: 5px;
            border: 1px solid #1abc9c;
            padding: 5px 10px;
            margin: 2px;
            transition: all 0.2s ease;
            width: 100%;
        }
        /* Specific style for the highlighted button */
        div.stButton button[data-testid="stButton-primary"] {
             background-color: #1abc9c;
             color: #FFFFFF;
        }
        </style>
        """
    st.markdown(style, unsafe_allow_html=True)
    
    # 設置按鈕類型以應用高亮樣式
    button_type = "primary" if is_selected else "secondary"
    
    if st.button(label, type=button_type, key=f"btn_{filter_key}_{value}"):
        # 如果點擊的按鈕已經被選中，則取消選擇
        if is_selected:
            st.session_state[filter_key] = 0
        else:
            st.session_state[filter_key] = value
        st.rerun()

# 簡化後的 display_info 函數：直接顯示文字內容
def display_info(label, value, is_fee=False):
    # 獲取顯示標籤 (可能包含百分比/費用的提示)
    display_label = LABEL_MAP.get(label, label) 
    display_value = "沒有" # 預設值

    if is_valid_data(value):
        val_str = str(value)
        
        # 處理網址
        if "網頁" in label and "http" in val_str:
            st.markdown(f"**{display_label}：** [{value}]({value})")
            return 
        else:
            # 直接顯示原始文字內容
            display_value = val_str
    
    elif is_fee:
        # 由於是純文字，我們不能確定它是 0 還是空，所以只在明確為學費/堂費/家教會費時顯示 $0
        if label in ["學費", "堂費", "家長教師會費"]:
             display_value = "$0"
        else:
             display_value = "沒有"
    
    elif label == "關聯學校":
        st.markdown(f"**{display_label}：** {display_value}")
        return

    st.markdown(f"**{display_label}：** {display_value}")
# --- [END] 輔助函數 ---


# --- [修改後] 側邊欄篩選函數定義 (保持不變) ---
def render_sidebar_filters(df):
    """
    在 Streamlit 側邊欄中呈現所有篩選器，無分類標題。
    """
    
    # 1. 區域篩選 (key="region")
    unique_regions = sorted(df['區域'].dropna().unique().tolist())
    st.sidebar.multiselect(
        "區域",
        options=unique_regions,
        default=st.session_state.get("region", []),
        key="region" 
    )

    # 2. 小一學校網篩選 (key="net")
    # 確保小一學校網為字串類型以進行正確篩選
    unique_school_nets = sorted(df['小一學校網'].dropna().unique().tolist())
    st.sidebar.multiselect(
        "小一學校網",
        options=unique_school_nets,
        default=st.session_state.get("net", []),
        key="net"
    )

    # 3. 資助類型篩選 (key="cat1")
    unique_types = sorted(df['資助類型'].dropna().unique().tolist())
    st.sidebar.multiselect(
        "資助類型",
        options=unique_types,
        default=st.session_state.get("cat1", []),
        key="cat1"
    )

    # 4. 學生性別篩選 (key="gender")
    unique_genders = sorted(df['學生性別'].dropna().unique().tolist())
    st.sidebar.multiselect(
        "學生性別",
        options=unique_genders,
        default=st.session_state.get("gender", []),
        key="gender"
    )
        
    # 5. 宗教篩選 (key="religion")
    unique_religions = sorted([r for r in df['宗教'].dropna().unique().tolist() if r not in ['不適用', '無']])
    st.sidebar.multiselect(
        "宗教背景",
        options=unique_religions,
        default=st.session_state.get("religion", []),
        key="religion"
    )

    # 6. 教學語言篩選 (key="lang")
    unique_languages = sorted(df['教學語言'].dropna().unique().tolist())
    st.sidebar.multiselect(
        "教學語言",
        options=unique_languages,
        default=st.session_state.get("lang", []),
        key="lang"
    )

    # 7. 關聯學校類型 (key="related")
    st.sidebar.multiselect(
        "關聯學校類型 (一條龍/直屬/聯繫)", 
        ["一條龍中學", "直屬中學", "聯繫中學"], 
        default=st.session_state.get("related", []),
        key="related"
    )

    # 8. 校車服務 (key="transport")
    st.sidebar.multiselect(
        "校車服務", 
        ["校車", "保姆車"], 
        default=st.session_state.get("transport", []),
        key="transport" 
    )
    
    pass
# --- [END] 側邊欄篩選函數定義 ---


school_df, article_df = load_data()

# --- 主應用程式 ---
if school_df is not None and article_df is not None:

    col_map = {
        "g1_tests": "全年全科測驗次數_一年級", "g1_exams": "全年全科考試次數_一年級",
        "g1_diverse_assessment": "小一上學期以多元化的進展性評估代替測驗及考試",
        "g2_6_tests": "全年全科測驗次數_二至六年級", "g2_6_exams": "全年全科考試次數_二至六年級",
        "tutorial_session": "按校情靈活編排時間表_盡量在下午安排導修時段_讓學生能在教師指導下完成部分家課",
        "no_test_after_holiday": "避免緊接在長假期後安排測考_讓學生在假期有充分的休息",
        "diverse_learning_assessment": "多元學習評估",
        "班級教學模式": "班級教學模式", 
        "分班安排": "分班安排"          
    }

    # 呼叫側邊欄篩選器
    render_sidebar_filters(school_df) 
    
    # 創建一個容器來顯示結果，並在按鈕點擊時清空並重新執行篩選
    results_container = st.container()
    
    # --- 篩選組件 (在按鈕上方) ---
    
    school_name_query = st.text_input(
        "根據學校名稱搜尋", 
        placeholder="請輸入學校名稱關鍵字...", 
        key="school_name_search"
    )
    
    with st.expander("根據課業安排篩選"):
        assessment_options = ["不限", "0次", "不多於1次", "不多於2次", "3次"]
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.selectbox("一年級測驗次數", assessment_options, key="g1_tests")
        with c2:
            st.selectbox("一年級考試次數", assessment_options, key="g1_exams")
        with c3:
            st.selectbox("二至六年級測驗次數", assessment_options, key="g2_6_tests")
        with c4:
            st.selectbox("二至六年級考試次數", assessment_options, key="g2_6_exams")

        c5, c6 = st.columns(2)
        with c5:
            st.checkbox("小一上學期以多元化評估代替測考", key="diverse")
        with c6:
            st.checkbox("下午設導修課 (教師指導家課)", key="tutorial")
    
    # --- [START] 師資按鈕篩選 UI (保持按鈕佈局) ---
    with st.expander("根據師資等級搜尋"):
        
        st.markdown("**碩士/博士或以上學歷 (%)**")
        col_master1, col_master2, col_master3 = st.columns(3)
        with col_master1: style_filter_button("最少 5%", 5, 'master_filter')
        with col_master2: style_filter_button("最少 15%", 15, 'master_filter')
        with col_master3: style_filter_button("最少 25%", 25, 'master_filter')

        st.markdown("**10年或以上年資 (%)**")
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        with col_exp1: style_filter_button("最少 20%", 20, 'exp_filter')
        with col_exp2: style_filter_button("最少 40%", 40, 'exp_filter')
        with col_exp3: style_filter_button("最少 60%", 60, 'exp_filter')
        
        st.markdown("**特殊教育培訓 (%)**")
        col_sen1, col_sen2, col_sen3 = st.columns(3)
        with col_sen1: style_filter_button("最少 10%", 10, 'sen_filter')
        with col_sen2: style_filter_button("最少 20%", 20, 'sen_filter')
        with col_sen3: style_filter_button("最少 30%", 30, 'sen_filter')
    # --- [END] 師資按鈕篩選 UI ---

    st.write("") 
    
    # 🚨 搜尋按鈕放在篩選組件區下方
    if st.button("🚀 搜尋學校", type="primary", use_container_width=True):
        
        mask = pd.Series(True, index=school_df.index)
        query = st.session_state.school_name_search.strip() if 'school_name_search' in st.session_state else ""
        
        # --- 讀取 SIDEBAR 篩選器值並應用過濾 (保持不變) ---
        selected_region = st.session_state.get("region", [])
        selected_net = st.session_state.get("net", [])
        selected_cat1 = st.session_state.get("cat1", [])
        selected_gender = st.session_state.get("gender", [])
        selected_religion = st.session_state.get("religion", [])
        selected_language = st.session_state.get("lang", [])
        selected_related = st.session_state.get("related", [])
        selected_transport = st.session_state.get("transport", [])
        
        if query: mask &= school_df["學校名稱"].str.contains(query, case=False, na=False)
        if selected_region: mask &= school_df["區域"].isin(selected_region)
        if selected_cat1: mask &= school_df["資助類型"].isin(selected_cat1)
        if selected_gender: mask &= school_df["學生性別"].isin(selected_gender)
        if selected_religion: mask &= school_df["宗教"].isin(selected_religion)
        if selected_language: mask &= school_df["教學語言"].isin(selected_language)
        # 確保 "小一學校網" 欄位被當作字串進行比較
        if selected_net: mask &= school_df["小一學校網"].isin(selected_net)
        
        if selected_related:
            related_mask = pd.Series(False, index=school_df.index)
            for col in selected_related:
                if col in school_df.columns: 
                    # 檢查欄位是否有有效數據 (is_valid_data)
                    related_mask |= school_df[col].apply(lambda x: is_valid_data(x))
                mask &= related_mask
        
        if selected_transport:
            transport_mask = pd.Series(False, index=school_df.index)
            for col in selected_transport:
                if col in school_df.columns: transport_mask |= (school_df[col] == "有")
            mask &= transport_mask
        # --- SIDEBAR 篩選結束 ---
        
        # --- 主體其他篩選邏輯 (🚨 重要：由於資料現為純文字，這裡的數值篩選將不再準確！) ---
        # 必須將篩選值轉換為字串來進行匹配
        
        def apply_assessment_filter_text(mask, column, selection):
            if selection == "0次": return mask & (school_df[column] == "0")
            elif selection == "不多於1次": 
                # 純文字無法進行 <= 1 比較，只能匹配 "1" 或 "0"
                return mask & ((school_df[column] == "1") | (school_df[column] == "0"))
            elif selection == "不多於2次": 
                # 純文字匹配 "2", "1", "0"
                return mask & ((school_df[column] == "2") | (school_df[column] == "1") | (school_df[column] == "0"))
            elif selection == "3次": return mask & (school_df[column] == "3")
            return mask
            
        selected_g1_tests = st.session_state.g1_tests if 'g1_tests' in st.session_state else "不限"
        selected_g1_exams = st.session_state.g1_exams if 'g1_exams' in st.session_state else "不限"
        selected_g2_6_tests = st.session_state.g2_6_tests if 'g2_6_tests' in st.session_state else "不限"
        selected_g2_6_exams = st.session_state.g2_6_exams if 'g2_6_exams' in st.session_state else "不限"
        use_diverse_assessment = st.session_state.diverse if 'diverse' in st.session_state else False
        has_tutorial_session = st.session_state.tutorial if 'tutorial' in st.session_state else False
        
        mask = apply_assessment_filter_text(mask, col_map["g1_tests"], selected_g1_tests)
        mask = apply_assessment_filter_text(mask, col_map["g1_exams"], selected_g1_exams)
        mask = apply_assessment_filter_text(mask, col_map["g2_6_tests"], selected_g2_6_tests)
        mask = apply_assessment_filter_text(mask, col_map["g2_6_exams"], selected_g2_6_exams)
        
        if use_diverse_assessment: mask &= (school_df[col_map["g1_diverse_assessment"]] == "是")
        if has_tutorial_session: mask &= (school_df[col_map["tutorial_session"]] == "有")
        
        # 師資按鈕篩選邏輯：純文字無法進行數字比較，暫時不做數值過濾
        
        st.session_state.filtered_schools = school_df[mask]

    # --- 結果顯示區 (不論是否點擊按鈕，只要 state 中有結果就顯示) ---
    if not st.session_state.filtered_schools.empty:
        
        # --- 內容組織變數定義 (移到迴圈外) ---
        fee_cols = ["學費", "堂費", "家長教師會費", "非標準項目的核准收費", "其他收費_費用", "學費減免"]
        teacher_stat_cols = [
            "已接受師資培訓人數百分率", "學士人數百分率", "碩士／博士或以上人數百分率", 
            "特殊教育培訓人數百分率", "0至4年年資人數百分率", "5至9年年資人數百分率", 
            "10年年資或以上人數百分率", "核准編制教師職位數目", "教師總人數", 
            "教師專業培訓及發展"
        ]
        
        facility_cols_counts = ["課室數目", "禮堂數目", "操場數目", "圖書館數目"]
        facility_cols_text = ["特別室", "其他學校設施", "支援有特殊教育需要學生的設施", "環保政策"]
        
        
        # 主分類 6: 辦學理念 (更新欄位列表, 移除被移動的)
        philosophy_display_cols = ["辦學宗旨", "學校管理架構", "法團校董會_校管會_校董會", "環保政策", "學校特色_其他", "校風", "學校發展計劃"]
        
        # 主分類 2: 學業評估與校園生活 (新增欄位列表)
        curriculum_cols = ["學校關注事項", "學習和教學策略", "小學教育課程更新重點的發展", "共通能力的培養", "正確價值觀_態度和行為的培養", "課程剪裁及調適措施"]
        collaboration_and_life_cols = ["家校合作", "健康校園生活", "全方位學習", "學校生活備註"]
        student_support_cols = ["全校參與照顧學生的多樣性", "全校參與模式融合教育", "非華語學生的教育支援"]
        
        # 確保 all_philosophy_cols 被正確定義
        all_philosophy_cols = ["校訓"] + philosophy_display_cols
        
        # --- 開始顯示結果 ---
        with results_container:
            st.divider()
            filtered_schools = st.session_state.filtered_schools
            st.subheader(f"篩選結果：共找到 {len(filtered_schools)} 間學校")
            
            if filtered_schools.empty:
                st.warning("找不到符合所有篩選條件的學校。")
            else:
                
                for index, row in filtered_schools.iterrows():
                    # 判斷是否有辦學理念資料
                    has_mission_data = any(is_valid_data(row.get(col)) for col in all_philosophy_cols)
                    
                    # 建立 tabs 列表
                    tab_list = ["基本資料", "學業評估與校園生活", "師資概況", "學校設施", "班級結構"]
                    if has_mission_data:
                        tab_list.append("辦學理念") 
                    tab_list.append("聯絡資料")
                    
                    with st.expander(f"**{row['學校名稱']}**"):
                        
                        # --- 相關文章 (不變) ---
                        related_articles = article_df[article_df["學校名稱"] == row["學校名稱"]] 
                        if not related_articles.empty:
                            with st.expander("相關文章", expanded=False): 
                                for _, article_row in related_articles.iterrows():
                                    title, link = article_row.get('文章標題'), article_row.get('文章連結')
                                    if pd.notna(title) and pd.notna(link):
                                        with st.container(border=True):
                                            st.markdown(f"[{title}]({link})")

                        tabs = st.tabs(tab_list)

                        # --- TAB 1: 基本資料 ---
                        with tabs[0]:
                            
                            # --- 學校概覽 (新增宗教、教學語言) ---
                            st.subheader("學校概覽")
                            c1, c2 = st.columns(2)
                            with c1: 
                                display_info("區域", row.get("區域"))
                                display_info("學校類別1", row.get("資助類型"))
                                display_info("創校年份", row.get("創校年份"))
                                display_info("宗教", row.get("宗教")) 
                                display_info("教學語言", row.get("教學語言")) 
                            with c2: 
                                display_info("小一學校網", row.get("小一學校網"))
                                display_info("學校類別2", row.get("上課時間"))
                                display_info("學生性別", row.get("學生性別"))
                                display_info("學校佔地面積", row.get("學校佔地面積"))
                            
                            # --- 校長與組織 ---
                            st.divider()
                            st.subheader("校長與組織")
                            c11, c12 = st.columns(2)
                            with c11:
                                principal_name = str(row.get("校長姓名", "")).strip()
                                principal_title = str(row.get("校長稱謂", "")).strip()
                                principal_display = f"{principal_name}{principal_title}" if is_valid_data(principal_name) else None
                                display_info("校長", principal_display)
                                display_info("辦學團體", row.get("辦學團體"))
                                display_info("家長教師會", row.get("家長教師會"))
                                display_info("法團校董會", row.get("法團校董會"))
                                display_info("校監和校董_校管會主席和成員的培訓達標率", row.get("校監和校董_校管會主席和成員的培訓達標率"))
                            with c12:
                                supervisor_name = str(row.get("校監_校管會主席姓名", "")).strip()
                                supervisor_title = str(row.get("校監_校管會主席稱謂", "")).strip()
                                supervisor_display = f"{supervisor_name}{supervisor_title}" if is_valid_data(supervisor_name) else None
                                display_info("校監_校管會主席姓名", supervisor_display)
                                display_info("舊生會_校友會", row.get("舊生會_校友會"))
                            
                            # --- 關聯學校 (原「關聯與交通」) ---
                            st.divider()
                            st.subheader("關聯學校")
                            related_dragon_val = row.get("一條龍中學")
                            related_feeder_val = row.get("直屬中學")
                            related_linked_val = row.get("聯繫中學")
                            
                            has_dragon = is_valid_data(related_dragon_val)
                            has_feeder = is_valid_data(related_feeder_val)
                            has_linked = is_valid_data(related_linked_val)
                            
                            if has_dragon or has_feeder or has_linked:
                                c_rel1, c_rel2, c_rel3 = st.columns(3)
                                with c_rel1: display_info("一條龍中學", related_dragon_val)
                                with c_rel2: display_info("直屬中學", related_feeder_val)
                                with c_rel3: display_info("聯繫中學", related_linked_val)
                            else:
                                st.info("沒有關聯學校資料。")


                            # --- 上學、午膳、放學、交通安排 (新增校車、保姆車) ---
                            st.divider()
                            st.subheader("上學、午膳、放學、交通安排")
                            
                            c_time1, c_time2 = st.columns(2)
                            with c_time1: display_info("上課時間_", row.get("上課時間_")) 
                            with c_time2: display_info("放學時間", row.get("放學時間")) 
                            
                            c_lunch1, c_lunch2 = st.columns(2)
                            with c_lunch1: display_info("午膳時間", row.get("午膳時間")) 
                            with c_lunch2: display_info("午膳結束時間", row.get("午膳結束時間"))
                            
                            c_lunch3, c_transport1, c_transport2 = st.columns(3)
                            with c_lunch3: display_info("午膳安排", row.get("午膳安排"))
                            
                            # NEW: 交通安排 (校車, 保姆車)
                            with c_transport1: display_info("校車", row.get("校車")) 
                            with c_transport2: display_info("保姆車", row.get("保姆車")) 


                            # --- 費用與資助 (新增學費減免) ---
                            st.divider()
                            st.subheader("費用與資助")
                            
                            c_fee1, c_fee2, c_fee3 = st.columns(3)
                            with c_fee1:
                                display_info("學費", row.get("學費"), is_fee=True)
                                display_info("非標準項目的核准收費", row.get("非標準項目的核准收費"), is_fee=True)
                            with c_fee2:
                                display_info("堂費", row.get("堂費"), is_fee=True)
                                display_info("其他收費_費用", row.get("其他收費_費用"), is_fee=True)
                            with c_fee3:
                                display_info("家長教師會費", row.get("家長教師會費"), is_fee=True)
                                display_info("學費減免", row.get("學費減免")) # NEW: 學費減免
                            
                            
                        # --- TAB 2: 學業評估與校園生活 (原: 學業評估與安排) ---
                        with tabs[1]:
                            st.subheader("學業評估與安排")
                            
                            st.markdown("##### 測驗與考試次數")
                            
                            # 測驗與考試次數 - HTML Table (顯示純文字)
                            assessment_table_html = f"""
                            <table class="clean-table assessment-table">
                                <thead>
                                    <tr>
                                        <th style="width: 35%;"></th>
                                        <th>測驗次數</th>
                                        <th>考試次數</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>一年級</td>
                                        <td>{display_assessment_count(row.get(col_map["g1_tests"]))}</td>
                                        <td>{display_assessment_count(row.get(col_map["g1_exams"]))}</td>
                                    </tr>
                                    <tr>
                                        <td>二至六年級</td>
                                        <td>{display_assessment_count(row.get(col_map["g2_6_tests"]))}</td>
                                        <td>{display_assessment_count(row.get(col_map["g2_6_exams"]))}</td>
                                    </tr>
                                </tbody>
                            </table>
                            """
                            st.markdown(assessment_table_html, unsafe_allow_html=True)
                            
                            st.divider()

                            st.markdown("##### 課業及教學模式")
                            
                            # 政策與教學模式 - HTML List
                            all_policy_data = [
                                ("g1_diverse_assessment", "小一上學期多元化評估"),
                                ("tutorial_session", "下午設導修課"),
                                ("no_test_after_holiday", "避免長假期後測考"),
                                ("分班安排", "分班安排"),
                                ("班級教學模式", "班級教學模式"),
                                ("diverse_learning_assessment", "多元學習評估"),
                            ]
                            
                            policy_list_html = ""
                            
                            for field_key, label in all_policy_data:
                                # 獲取值，並將內部的 \n 轉換為 <br>
                                value = str(row.get(field_key, "沒有")).replace('\n', '<br>')
                                
                                # 使用 CSS class 模擬 Key-Value 列表
                                policy_list_html += f"""
                                    <div class="policy-list-item">
                                        <strong>{label}：</strong>{value}
                                    </div>
                                """
                            
                            st.markdown(policy_list_html, unsafe_allow_html=True)
                            
                            # --- 課程發展與策略 ---
                            st.divider()
                            st.subheader("課程發展與策略")
                            for col in curriculum_cols:
                                display_info(col, row.get(col))

                            # --- 協作與校園生活 (Moved) ---
                            st.divider()
                            st.subheader("協作與校園生活")
                            for col in collaboration_and_life_cols:
                                display_info(col, row.get(col))

                            # --- 學生支援與關顧 (Moved) ---
                            st.divider()
                            st.subheader("學生支援與關顧")
                            for col in student_support_cols:
                                display_info(col, row.get(col))

                                
                        # --- TAB 3: 師資概況 ---
                        with tabs[2]:
                            st.subheader("師資團隊數字")
                            
                            # 1. 師資團隊數字 (顯示純文字)
                            c1, c2 = st.columns(2)
                            with c1:
                                display_info("核准編制教師職位數目", row.get("核准編制教師職位數目")) 
                            with c2:
                                display_info("教師總人數", row.get("教師總人數"))

                            st.divider()
                            st.subheader("教師團隊學歷及年資") 
                            
                            col_left, col_right = st.columns(2)

                            # --- 1. ACADEMICS/TRAINING DATA GENERATION (顯示純文字) ---
                            qual_cols_map = {
                                "已接受師資培訓人數百分率": "已接受師資培訓 (%)", 
                                "學士人數百分率": "學士學位 (%)", 
                                "碩士／博士或以上人數百分率": "碩士/博士學位 (%)", 
                                "特殊教育培訓人數百分率": "特殊教育培訓 (%)"
                            }
                            qual_rows_html = ""
                            for col_name, display_label in qual_cols_map.items():
                                value = row.get(col_name, "-")
                                display_value = value
                                qual_rows_html += f"""<tr><td>{display_label}</td><td>{display_value}</td></tr>"""
                            
                            # --- 2. SENIORITY DATA GENERATION (顯示純文字) ---
                            seniority_cols_map = {
                                "0至4年年資人數百分率": "0-4年年資 (%)", 
                                "5至9年年資人數百分率": "5-9年年資 (%)", 
                                "10年年資或以上人數百分率": "10+年年資 (%)"
                            }
                            seniority_rows_html = ""
                            for col_name, display_label in seniority_cols_map.items():
                                value = row.get(col_name, "-")
                                display_value = value
                                seniority_rows_html += f"""<tr><td>{display_label}</td><td>{display_value}</td></tr>"""

                            # Combine and display
                            with col_left:
                                st.markdown(f"""
                                    <div style="font-weight: bold; margin-bottom: 8px;">學歷及培訓</div>
                                    <table class="info-table">
                                        {qual_rows_html}
                                    </table>
                                """, unsafe_allow_html=True)
                                
                            with col_right:
                                 st.markdown(f"""
                                    <div style="font-weight: bold; margin-bottom: 8px;">年資分佈</div>
                                    <table class="info-table">
                                        {seniority_rows_html}
                                    </table>
                                """, unsafe_allow_html=True)

                            st.divider()
                            display_info("教師專業培訓及發展", row.get("教師專業培訓及發展"))


                        # --- TAB 4: 學校設施 ---
                        with tabs[3]:
                            st.subheader("設施數量")
                            # 1. 顯示數量統計 (顯示純文字)
                            col_count1, col_count2 = st.columns(2)
                            with col_count1:
                                display_info("課室數目", row.get("課室數目"))
                                display_info("操場數目", row.get("操場數目"))
                            with col_count2:
                                display_info("禮堂數目", row.get("禮堂數目"))
                                display_info("圖書館數目", row.get("圖書館數目"))
                            
                            st.divider()
                            st.subheader("設施詳情與環境政策")
                            # 2. 顯示詳情 (顯示純文字)
                            facility_cols_text_new = ["特別室", "其他學校設施", "支援有特殊教育需要學生的設施", "環保政策"]
                            
                            for col in facility_cols_text_new:
                                display_info(col, row.get(col))

                        # --- TAB 5: 班級結構 ---
                        with tabs[4]:
                            st.subheader("班級結構")
                            grades_internal = ["小一", "小二", "小三", "小四", "小五", "小六", "總"]
                            # 班級數值將以純文字形式讀取
                            last_year_data = [row.get(f"上學年{g}班數", "-") for g in grades_internal]
                            this_year_data = [row.get(f"本學年{g}班數", "-") for g in grades_internal]
                            
                            # 班級結構 - HTML Table (顯示純文字)
                            class_table_html = f"""
                            <table class="clean-table class-table">
                                <thead>
                                    <tr>
                                        <th></th>
                                        <th>小一</th>
                                        <th>小二</th>
                                        <th>小三</th>
                                        <th>小四</th>
                                        <th>小五</th>
                                        <th>小六</th>
                                        <th>總數</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>**上學年班數**</td>
                                        <td style="text-align: center;">{last_year_data[0]}</td>
                                        <td style="text-align: center;">{last_year_data[1]}</td>
                                        <td style="text-align: center;">{last_year_data[2]}</td>
                                        <td style="text-align: center;">{last_year_data[3]}</td>
                                        <td style="text-align: center;">{last_year_data[4]}</td>
                                        <td style="text-align: center;">{last_year_data[5]}</td>
                                        <td style="text-align: center;">**{last_year_data[6]}**</td>
                                    </tr>
                                    <tr>
                                        <td>**本學年班數**</td>
                                        <td style="text-align: center;">{this_year_data[0]}</td>
                                        <td style="text-align: center;">{this_year_data[1]}</td>
                                        <td style="text-align: center;">{this_year_data[2]}</td>
                                        <td style="text-align: center;">{this_year_data[3]}</td>
                                        <td style="text-align: center;">{this_year_data[4]}</td>
                                        <td style="text-align: center;">{this_year_data[5]}</td>
                                        <td style="text-align: center;">**{this_year_data[6]}**</td>
                                    </tr>
                                </tbody>
                            </table>
                            """
                            st.markdown(class_table_html, unsafe_allow_html=True)

                        # --- 動態 TABS: 辦學理念 (Tab index 5 或 6) ---
                        tab_index = 5
                        if has_mission_data:
                            with tabs[tab_index]:
                                st.subheader("辦學理念")
                                # 顯示校訓
                                display_info("校訓", row.get("校訓"))
                                
                                # 顯示辦學宗旨、學校關注事項、學校特色等核心理念 (更新為 philosophy_display_cols)
                                for col in philosophy_display_cols:
                                    if col != "校訓": # 避免重複顯示
                                        display_info(col, row.get(col))
                                
                            tab_index += 1
                        
                        with tabs[tab_index]:
                            st.subheader("聯絡資料")
                            c1, c2 = st.columns(2)
                            with c1:
                                display_info("地址", row.get("學校地址"))
                                display_info("傳真", row.get("學校傳真"))
                            with c2:
                                display_info("電話", row.get("學校電話"))
                                display_info("電郵", row.get("學校電郵"))
                            display_info("網頁", row.get("學校網址"))
                        
                        # --- [END] TABS 結構 ---

                # 🚨 放在搜尋結果的下方：回到最頂按鈕
                st.divider()
                if st.button("⬆️ 回到最頂", use_container_width=True):
                    # 使用 st.rerun 模擬回到頂部的效果
                    st.rerun()
