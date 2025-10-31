import streamlit as st
import pandas as pd
import numpy as np

# --- 頁面設定 ---
st.set_page_config(page_title="香港小學選校篩選器", layout="wide")

# --- 注入 CSS 實現 Tab 滾動提示、表格樣式及側邊欄按鈕優化 ---
st.markdown("""
    <style>
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

# --- 主標題 ---
st.title("香港小學選校篩選器")

# --- 初始化 Session State ---
if 'search_mode' not in st.session_state:
    st.session_state.search_mode = False 
if 'filtered_schools' not in st.session_state:
    st.session_state.filtered_schools = pd.DataFrame()

# 初始化篩選器按鈕狀態 (Filter buttons)
if 'master_filter' not in st.session_state:
    st.session_state.master_filter = 0
if 'exp_filter' not in st.session_state:
    st.session_state.exp_filter = 0
if 'sen_filter' not in st.session_state:
    st.session_state.sen_filter = 0

# --- 載入與處理資料 ---
@st.cache_data
def load_data():
    try:
        # 使用您最新的檔案名稱
        school_df = pd.read_csv("database_school_info.csv") 
        article_df = pd.read_csv("database_related_article.csv")
        
        school_df.columns = school_df.columns.str.strip()
        article_df.columns = article_df.columns.str.strip()
        
        school_df.rename(columns={"學校類別1": "資助類型", "學校類別2": "上課時間"}, inplace=True)
        
        # 強制清理時間欄位 (CC, CD, CE, CF)
        time_cols_to_clean = ["上課時間_", "放學時間", "午膳時間", "午膳結束時間"]
        for col in time_cols_to_clean:
            if col in school_df.columns:
                # 強制轉為 string 並移除前後空格
                school_df[col] = school_df[col].astype(str).str.strip()

        for col in school_df.select_dtypes(include=['object']).columns:
            if col not in time_cols_to_clean and school_df[col].dtype == 'object':
                school_df[col] = school_df[col].str.replace('<br>', '\n', regex=False).str.strip()
        
        if '學校名稱' in school_df.columns:
            school_df['學校名稱'] = school_df['學校名稱'].str.replace(r'\s+', ' ', regex=True).str.strip()

        fee_columns = ["學費", "堂費", "家長教師會費"]
        for col in fee_columns:
            if col in school_df.columns:
                school_df[col] = pd.to_numeric(school_df[col].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce').fillna(0)

        # 這裡調整了百分比欄位的名稱，以確保與您的數據一致
        teacher_stat_cols = [
            "已接受師資培訓人數百分率", "學士人數百分率", 
            "碩士／博士或以上人數百分率", "特殊教育培訓人數百分率",
            "0至4年年資人數百分率", "5至9年年資人數百分率", 
            "10年年資或以上人數百分率"
        ]
        
        # 修正列名中可能的"培训"到"培訓"的差異 (若原始CSV使用"培训")
        if "已接受師資培训人數百分率" in school_df.columns and "已接受師資培訓人數百分率" not in school_df.columns:
             school_df.rename(columns={"已接受師資培训人數百分率": "已接受師資培訓人數百分率"}, inplace=True)
        
        for col in teacher_stat_cols:
            if col in school_df.columns:
                school_df[col] = pd.to_numeric(school_df[col].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce').fillna(0)

        # === 解決方案：教師人數欄位轉換邏輯 (修復讀取問題) ===
        teacher_count_cols_all = ["核准編制教師職位數目", "教師總人數", "上學年核准編制教師職位數目", "上學年教師總人數"] 
        
        for col in teacher_count_cols_all:
            if col in school_df.columns:
                # 1. 移除數字以外的雜項字符 (保留數字和小數點)
                cleaned_series = school_df[col].astype(str).str.replace('[^0-9.]', '', regex=True)
                # 2. 強制轉換為數字型態，無法轉換的設為 NaN
                school_df[col] = pd.to_numeric(cleaned_series, errors='coerce')
                # 3. 填補 NaN 為 0，並轉換為整數
                school_df[col] = school_df[col].fillna(0).astype(int)
        # === 解決方案：新增教師人數欄位轉換邏輯 END ===
        
        assessment_cols = ["全年全科測驗次數_一年級", "全年全科考試次數_一年級", "全年全科測驗次數_二至六年級", "全年全科考試次數_二至六年級"]
        for col in assessment_cols:
            if col in school_df.columns:
                school_df[col] = pd.to_numeric(school_df[col], errors='coerce').fillna(0).astype(int)
        
        for year in ["上學年", "本學年"]:
            for grade in ["小一", "小二", "小三", "小四", "小五", "小六", "總"]:
                col_name = f"{year}{grade}班數"
                if col_name in school_df.columns:
                    school_df[col_name] = pd.to_numeric(school_df[col_name], errors='coerce').fillna(0).astype(int)
        
        if "學校佔地面積" in school_df.columns:
            school_df["學校佔地面積"] = pd.to_numeric(school_df["學校佔地面積"], errors='coerce').fillna(0)

        return school_df, article_df
        
    except FileNotFoundError:
        st.error("錯誤：找不到資料檔案。請確保 'database_school_info.csv' 和 'database_related_article.csv' 檔案與 app.py 在同一個資料夾中。")
        return None, None
    except Exception as e:
        st.error(f"處理資料時發生錯誤：{e}。請檢查您的 CSV 檔案格式是否正確。")
        return None, None

# --- [START] 輔助函數 ---
# 這裡修改 LABEL_MAP 以移除百分比符號，滿足圖表類別標籤的要求
LABEL_MAP = { 
    "校監_校管會主席姓名": "校監", 
    "校長姓名": "校長",
    "舊生會_校友會": "舊生會／校友會", 
    "上課時間_": "一般上學時間",
    "放學時間": "一般放學時間",
    "午膳時間": "午膳開始時間",
    "午膳結束時間": "午膳結束時間",
    "核准編制教師職位數目": "核准編制教師職位數目", # CSV 實際名稱
    "教師總人數": "教師總人數", # CSV 實際名稱
    "上學年核准編制教師職位數目": "核准編制教師職位數目", # Tab 3 曾使用的錯誤名稱
    "上學年教師總人數": "教師總人數", # Tab 3 曾使用的錯誤名稱
    "已接受師資培訓人數百分率": "已接受師資培訓", 
    "學士人數百分率": "學士學位",
    "碩士／博士或以上人數百分率": "碩士/博士學位",
    "特殊教育培訓人數百分率": "特殊教育培訓",
    "0至4年年資人數百分率": "0-4年年資", 
    "5至9年年資人數百分率": "5-9年年資", 
    "10年年資或以上人數百分率": "10+年年資", 
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
    "聯繫中學": "聯繫中學"
}

def is_valid_data(value):
    return pd.notna(value) and str(value).strip() and str(value).lower() not in ['nan', '-']

# 僅顯示評估數字
def display_assessment_count(value):
    if is_valid_data(value) and isinstance(value, (int, float)):
        return f"{int(value)}"
    return "-"

# 格式化篩選器按鈕的高亮樣式 (Filter Buttons)
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

# 更新 display_info 函數以始終顯示標籤
def display_info(label, value, is_fee=False):
    # 關鍵：這裡我們使用 label 來檢查是哪個欄位
    display_label = LABEL_MAP.get(label, label) 
    display_value = "沒有" # 預設值
    is_time_field = label in ["上課時間_", "放學時間", "午膳時間", "午膳結束時間"]

    if is_valid_data(value):
        val_str = str(value)
        # 檢查是否為百分比欄位 (通過檢查原始 key 是否包含 "百分率")
        is_percentage_field = '百分率' in label 
        
        if "網頁" in label and "http" in val_str:
            st.markdown(f"**{display_label}：** [{value}]({value})")
            return 
        elif is_percentage_field and isinstance(value, (int, float)):
            # 文本顯示中不帶 %, 僅數字 (例如 98.5)
            display_value = f"{value:.1f}"
        elif is_fee:
            if isinstance(value, (int, float)) and value > 0:
                display_value = f"${int(value)}"
            elif isinstance(value, (int, float)) and value == 0:
                display_value = "$0"
            else:
                display_value = val_str
        elif is_time_field and ':' in val_str:
            # 時間格式化邏輯
            try:
                parts = val_str.split(':')
                if len(parts) >= 2:
                    display_value = f"{parts[0]}:{parts[1]}"
                else:
                    display_value = val_str
            except:
                display_value = val_str
        else:
            # 處理所有非百分比的數字欄位 (包括修復後的教師人數)
            if isinstance(value, (int, float)):
                display_value = str(int(value))
            else:
                display_value = val_str
    
    elif is_fee:
        if label in ["學費", "堂費", "家長教師會費"]:
             display_value = "$0"
        else:
             display_value = "沒有"
    
    elif label == "關聯學校":
        st.markdown(f"**{display_label}：** {display_value}")
        return

    st.markdown(f"**{display_label}：** {display_value}")
# --- [END] 輔助函數 ---


# --- [修改後] 側邊欄篩選函數定義 (無標題/分隔線) ---
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
    unique_school_nets = sorted(df['小一學校網'].astype(str).dropna().unique().tolist())
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
        "policy_on_web": "將校本課業政策上載至學校網頁_讓公眾及持份者知悉",
        "homework_policy": "制定適切的校本課業政策_讓家長了解相關安排_並定期蒐集教師_學生和家長的意見",
        "diverse_learning_assessment": "多元學習評估",
        "班級教學模式": "班級教學模式", 
        "分班安排": "分班安排"          
    }

    if not st.session_state.search_mode:
        
        # 呼叫側邊欄篩選器
        render_sidebar_filters(school_df) 
        
        school_name_query = st.text_input(
            "根據學校名稱搜尋", 
            placeholder="請輸入學校名稱關鍵字...", 
            key="school_name_search"
        )
        
        # --- 原有的基本篩選器 Expander 已移除 ---

        with st.expander("根據課業安排篩選"):
            assessment_options = ["不限", "0次", "不多於1次", "不多於2次", "3次"]
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                selected_g1_tests = st.selectbox("一年級測驗次數", assessment_options, key="g1_tests")
            with c2:
                selected_g1_exams = st.selectbox("一年級考試次數", assessment_options, key="g1_exams")
            with c3:
                selected_g2_6_tests = st.selectbox("二至六年級測驗次數", assessment_options, key="g2_6_tests")
            with c4:
                selected_g2_6_exams = st.selectbox("二至六年級考試次數", assessment_options, key="g2_6_exams")

            c5, c6 = st.columns(2)
            with c5:
                use_diverse_assessment = st.checkbox("小一上學期以多元化評估代替測考", key="diverse")
            with c6:
                has_tutorial_session = st.checkbox("下午設導修課 (教師指導家課)", key="tutorial")
        
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
        if st.button("🚀 搜尋學校", type="primary", use_container_width=True):
            st.session_state.search_mode = True
            
            mask = pd.Series(True, index=school_df.index)
            query = school_name_query.strip()
            
            # --- 讀取 SIDEBAR 篩選器值並應用過濾 ---
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
            if selected_net: mask &= school_df["小一學校網"].astype(str).isin([str(n) for n in selected_net])
            
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
            
            # --- 主體其他篩選邏輯 (保持不變) ---
            def apply_assessment_filter(mask, column, selection):
                if selection == "0次": return mask & (school_df[column] == 0)
                elif selection == "不多於1次": return mask & (school_df[column] <= 1)
                elif selection == "不多於2次": return mask & (school_df[column] <= 2)
                elif selection == "3次": return mask & (school_df[column] == 3)
                return mask
                
            mask = apply_assessment_filter(mask, col_map["g1_tests"], selected_g1_tests)
            mask = apply_assessment_filter(mask, col_map["g1_exams"], selected_g1_exams)
            mask = apply_assessment_filter(mask, col_map["g2_6_tests"], selected_g2_6_tests)
            mask = apply_assessment_filter(mask, col_map["g2_6_exams"], selected_g2_6_exams)
            
            if use_diverse_assessment: mask &= (school_df[col_map["g1_diverse_assessment"]] == "是")
            if has_tutorial_session: mask &= (school_df[col_map["tutorial_session"]] == "有")
            
            # 師資按鈕篩選邏輯
            if st.session_state.master_filter > 0:
                mask &= (school_df["碩士_博士或以上人數百分率"] >= st.session_state.master_filter)
            if st.session_state.exp_filter > 0:
                mask &= (school_df["10年年資或以上人數百分率"] >= st.session_state.exp_filter)
            if st.session_state.sen_filter > 0:
                mask &= (school_df["特殊教育培訓人數百分率"] >= st.session_state.sen_filter)
            # --- 主體其他篩選邏輯結束 ---

            st.session_state.filtered_schools = school_df[mask]
            st.rerun()

    else:
        # --- [START] 結果頁面：切換回 ST.TABS 結構 ---
        if st.button("✏️ 返回並修改篩選條件"):
            st.session_state.search_mode = False
            st.rerun()

        st.divider()
        filtered_schools = st.session_state.filtered_schools
        st.subheader(f"篩選結果：共找到 {len(filtered_schools)} 間學校")
        
        if filtered_schools.empty:
            st.warning("找不到符合所有篩選條件的學校。")
        else:
            # 欄位定義 (保持不變)
            fee_cols = ["學費", "堂費", "家長教師會費", "非標準項目的核准收費", "其他收費_費用"]
            teacher_stat_cols = [
                "已接受師資培訓人數百分率", "學士人數百分率", "碩士／博士或以上人數百分率", 
                "特殊教育培訓人數百分率", "0至4年年資人數百分率", "5至9年年資人數百分率", 
                "10年年資或以上人數百分率", "核准編制教師職位數目", "教師總人數", 
                "教師專業培訓及發展"
            ]
            other_categories = {
                "辦學理念": ["辦學宗旨", "學校關注事項", "學校特色"],
            }
            facility_cols_counts = ["課室數目", "禮堂數目", "操場數目", "圖書館數目"]
            facility_cols_text = ["特別室", "其他學校設施", "支援有特殊教育需要學生的設施"]
            assessment_display_map = {
                "g1_diverse_assessment": "小一上學期多元化評估",
                "tutorial_session": "下午設導修課",
                "no_test_after_holiday": "避免長假期後測考",
                "policy_on_web": "網上校本課業政策",
                "homework_policy": "制定校本課業政策",
                "班級教學模式": "班級教學模式",
                "分班安排": "分班安排",
                "diverse_learning_assessment": "多元學習評估" 
            }
            
            for index, row in filtered_schools.iterrows():
                # 檢查是否有辦學理念數據
                has_mission_data = any(is_valid_data(row.get(col)) for col in other_categories["辦學理念"])
                
                # 建立 tabs 列表
                tab_list = ["基本資料", "學業評估與安排", "師資概況", "學校設施", "班級結構"]
                if has_mission_data:
                    tab_list.append("辦學理念與補充資料")
                tab_list.append("聯絡資料")
                
                with st.expander(f"**{row['學校名稱']}**"):
                    
                    # --- 相關文章 ---
                    # 修正 NameError: related_articles 應為 article_df
                    related_articles = article_df[article_df["學校名稱"] == row["學校名稱"]] 
                    if not related_articles.empty:
                        with st.expander("相關文章", expanded=False): 
                            for _, article_row in related_articles.iterrows():
                                title, link = article_row.get('文章標題'), article_row.get('文章連結')
                                if pd.notna(title) and pd.notna(link):
                                    with st.container(border=True):
                                        st.markdown(f"[{title}]({link})")

                    tabs = st.tabs(tab_list)

                    # --- TAB 1: 基本資料 (保持不變) ---
                    with tabs[0]:
                        st.subheader("學校基本資料")
                        # 佈局基於 DOCX 格式
                        c1, c2 = st.columns(2)
                        with c1: display_info("區域", row.get("區域"))
                        with c2: display_info("小一學校網", row.get("小一學校網"))
                        
                        c3, c4 = st.columns(2)
                        with c3: display_info("資助類型", row.get("資助類型"))
                        with c4: display_info("學生性別", row.get("學生性別"))

                        c5, c6 = st.columns(2)
                        with c5: display_info("創校年份", row.get("創校年份"))
                        with c6: display_info("辦學團體", row.get("辦學團體"))

                        c7, c8 = st.columns(2)
                        with c7: display_info("宗教", row.get("宗教"))
                        with c8: display_info("學校佔地面積", row.get("學校佔地面積"))

                        c9, c10 = st.columns(2)
                        with c9: display_info("教學語言", row.get("教學語言"))
                        
                        # 關聯學校邏輯
                        with c10: 
                            related_dragon_val = row.get("一條龍中學")
                            related_feeder_val = row.get("直屬中學")
                            related_linked_val = row.get("聯繫中學")
                            
                            has_dragon = is_valid_data(related_dragon_val)
                            has_feeder = is_valid_data(related_feeder_val)
                            has_linked = is_valid_data(related_linked_val)

                            if not has_dragon and not has_feeder and not has_linked:
                                display_info("關聯學校", None)
                            else:
                                st.markdown("**關聯學校：**")
                                if has_dragon:
                                    display_info("一條龍中學", related_dragon_val)
                                if has_feeder:
                                    display_info("直屬中學", related_feeder_val)
                                if has_linked:
                                    display_info("聯繫中學", related_linked_val)

                        c11, c12 = st.columns(2)
                        with c11:
                            principal_name = str(row.get("校長姓名", "")).strip()
                            principal_title = str(row.get("校長稱謂", "")).strip()
                            principal_display = f"{principal_name}{principal_title}" if is_valid_data(principal_name) else None
                            display_info("校長", principal_display)
                        with c12:
                            supervisor_name = str(row.get("校監_校管會主席姓名", "")).strip()
                            supervisor_title = str(row.get("校監_校管會主席稱謂", "")).strip()
                            supervisor_display = f"{supervisor_name}{supervisor_title}" if is_valid_data(supervisor_name) else None
                            display_info("校監_校管會主席姓名", supervisor_display)

                        c13, c14 = st.columns(2)
                        with c13: display_info("家長教師會", row.get("家長教師會"))
                        with c14: display_info("舊生會_校友會", row.get("舊生會_校友會"))

                        st.divider()
                        st.subheader("上學及放學安排")
                        
                        c_transport1, c_transport2 = st.columns(2)
                        with c_transport1:
                            has_bus, has_van = row.get("校車") == "有", row.get("保姆車") == "有"
                            transport_status = "沒有"
                            if has_bus and has_van: transport_status = "有校車及保姆車"
                            elif has_bus: transport_status = "有校車"
                            elif has_van: transport_status = "有保姆車"
                            display_info("校車或保姆車", transport_status)
                        
                        c15, c16 = st.columns(2)
                        with c15: display_info("上課時間_", row.get("上課時間_"))
                        with c16: display_info("放學時間", row.get("放學時間"))

                        st.divider()
                        st.subheader("午膳安排")
                        
                        c_lunch1, c_lunch2 = st.columns(2)
                        with c_lunch1: display_info("午膳安排", row.get("午膳安排"))
                        
                        c17, c18 = st.columns(2)
                        with c17: display_info("午膳時間", row.get("午膳時間"))
                        with c18: display_info("午膳結束時間", row.get("午膳結束時間"))

                        st.divider()
                        st.subheader("費用")
                        
                        for col_key in fee_cols:
                            display_info(col_key, row.get(col_key), is_fee=True)
                        
                    # --- TAB 2: 學業評估與安排 (保持不變) ---
                    with tabs[1]:
                        st.subheader("學業評估與安排")
                        
                        st.markdown("##### 測驗與考試次數")
                        
                        # 測驗與考試次數 - HTML Table (已修正錯位問題)
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

                        st.markdown("##### 課業及教學政策")
                        
                        # 政策與教學模式 - HTML Table (已修正為最終優化列表)
                        
                        # 1. 定義數據和標籤的列表 (確保順序與 DOCX 格式一致)
                        all_policy_data = [
                            ("g1_diverse_assessment", "小一上學期多元化評估"),
                            ("tutorial_session", "下午設導修課"),
                            ("homework_policy", "制定校本課業政策"),
                            ("no_test_after_holiday", "避免長假期後測考"),
                            ("分班安排", "分班安排"),
                            ("班級教學模式", "班級教學模式"),
                            ("diverse_learning_assessment", "多元學習評估"),
                            ("policy_on_web", "網上校本課業政策"),
                        ]
                        
                        # 2. 建立 HTML 列表內容
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
                            
                    # --- TAB 3: 師資概況 (已修復 NameError 並使用 HTML 表格重組) ---
                    with tabs[2]:
                        st.subheader("師資團隊數字")
                        
                        # 1. 師資團隊數字 (Numbers)
                        c1, c2 = st.columns(2)
                        with c1:
                            # 使用 CSV 實際名稱
                            display_info("核准編制教師職位數目", row.get("核准編制教師職位數目")) 
                        with c2:
                            display_info("教師總人數", row.get("教師總人數"))

                        st.divider()
                        st.subheader("教師團隊學歷及年資") 
                        
                        col_left, col_right = st.columns(2)

                        # --- 1. ACADEMICS/TRAINING DATA GENERATION ---
                        qual_cols_map = {
                            "已接受師資培訓人數百分率": "已接受師資培訓", 
                            "學士人數百分率": "學士學位", 
                            "碩士／博士或以上人數百分率": "碩士/博士學位", 
                            "特殊教育培訓人數百分率": "特殊教育培訓"
                        }
                        qual_rows_html = ""
                        for col_name, display_label in qual_cols_map.items():
                            value = row.get(col_name, 0)
                            # 格式化為 X.X%
                            display_value = f"{value:.1f}％"
                            qual_rows_html += f"""
<tr>
    <td>{display_label}</td>
    <td>{display_value}</td>
</tr>
"""
                        
                        # --- 2. SENIORITY DATA GENERATION ---
                        seniority_cols_map = {
                            "0至4年年資人數百分率": "0-4年年資", 
                            "5至9年年資人數百分率": "5-9年年資", 
                            "10年年資或以上人數百分率": "10+年年資"
                        }
                        seniority_rows_html = ""
                        for col_name, display_label in seniority_cols_map.items():
                            value = row.get(col_name, 0)
                            # 格式化為 X.X%
                            display_value = f"{value:.1f}％"
                            seniority_rows_html += f"""
<tr>
    <td>{display_label}</td>
    <td>{display_value}</td>
</tr>
"""

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


                    # --- TAB 4: 學校設施 (已簡化並移除標題與分隔線) ---
                    with tabs[3]:
                        # 1. 顯示數量統計 (直接顯示，無標題)
                        col_count1, col_count2 = st.columns(2)
                        with col_count1:
                            display_info("課室數目", row.get("課室數目"))
                            display_info("操場數目", row.get("操場數目"))
                        with col_count2:
                            display_info("禮堂數目", row.get("禮堂數目"))
                            display_info("圖書館數目", row.get("圖書館數目"))
                        
                        # 2. 顯示詳情 (直接顯示，無標題和分隔線)
                        facility_cols_text_new = ["特別室", "其他學校設施", "支援有特殊教育需要學生的設施"]
                        
                        for col in facility_cols_text_new:
                            # 使用 display_info 確保格式統一
                            display_info(col, row.get(col))

                    # --- TAB 5: 班級結構 ---
                    with tabs[4]:
                        st.subheader("班級結構")
                        grades_display = ["小一", "小二", "小三", "小四", "小五", "小六", "總數"]
                        grades_internal = ["小一", "小二", "小三", "小四", "小五", "小六", "總"]
                        last_year_data = [row.get(f"上學年{g}班數", 0) for g in grades_internal]
                        this_year_data = [row.get(f"本學年{g}班數", 0) for g in grades_internal]
                        
                        # 班級結構 - HTML Table (已修正)
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

                    # --- 動態 TABS ---
                    tab_index = 5
                    if has_mission_data:
                        with tabs[tab_index]:
                            st.subheader("辦學理念")
                            for col in other_categories["辦學理念"]:
                                display_info(col, row.get(col))
                            
                            st.divider()
                            st.subheader("其他補充資料")
                            
                            # 建立排除列表 (已顯示的欄位)
                            displayed_cols = set(fee_cols + teacher_stat_cols + list(other_categories["辦學理念"]) + facility_cols_counts + facility_cols_text + list(assessment_display_map.values()) + ["區域", "小一學校網", "資助類型", "學生性別", "創校年份", "宗教", "教學語言", "校車", "保姆車", "辦學團體", "校訓", "校長姓名", "校長稱謂", "校監_校管會主席姓名", "校監_校管會主席稱謂", "家長教師會", "舊生會_校友會", "一條龍中學", "直屬中學", "聯繫中學", "上課時間", "上課時間_", "放學時間", "午膳安排", "午膳時間", "午膳結束時間", "學校名稱", "學校地址", "學校電話", "學校傳真", "學校電郵", "學校網址", "學校佔地面積", "核准編制教師職位數目", "教師總人數", "上學年核准編制教師職位數目", "上學年教師總人數"])
                            for i in range(1, 7):
                                displayed_cols.add(f"上學年小{i}班數")
                                displayed_cols.add(f"本學年小{i}班數")
                            displayed_cols.add("上學年總班數")
                            displayed_cols.add("本學年總班數")

                            other_cols_exist = False
                            for col_name in school_df.columns:
                                if col_name not in displayed_cols:
                                    value = row.get(col_name)
                                    if is_valid_data(value):
                                        display_info(col_name, value)
                                        other_cols_exist = True
                            if not other_cols_exist:
                                st.info("沒有其他補充資料可顯示。")
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
