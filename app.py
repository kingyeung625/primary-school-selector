import streamlit as st
import pandas as pd
import numpy as np

# --- 頁面設定 ---
st.set_page_config(page_title="香港小學選校篩選器", layout="wide")

# --- 主標題 ---
st.title("香港小學選校篩選器")

# --- 載入與處理資料 ---
@st.cache_data
def load_data():
    try:
        school_df = pd.read_csv("database - 學校資料.csv")
        article_df = pd.read_csv("database - 相關文章.csv")
        
        school_df.rename(columns={"學校類別1": "資助類型", "學校類別2": "上課時間"}, inplace=True)
        
        # 數據清理
        fee_columns = ["學費", "堂費"]
        for col in fee_columns:
            if col in school_df.columns:
                school_df[col] = pd.to_numeric(school_df[col].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce').fillna(0)

        assessment_cols = [
            "全年全科測驗次數_一年級", "全年全科考試次數_一年級",
            "全年全科測驗次數_二至六年級", "全年全科考試次數_二至六年級"
        ]
        for col in assessment_cols:
            if col in school_df.columns:
                school_df[col] = pd.to_numeric(school_df[col], errors='coerce').fillna(0).astype(int)
        
        # 清理班級數目，確保為數字
        for year in ["上學年", "本學年"]:
            for grade in ["小一", "小二", "小三", "小四", "小五", "小六", "總"]:
                col_name = f"{year}{grade}班數"
                if col_name in school_df.columns:
                    school_df[col_name] = pd.to_numeric(school_df[col_name], errors='coerce').fillna(0).astype(int)

        return school_df, article_df
        
    except FileNotFoundError:
        st.error("錯誤：找不到資料檔案。請確保 'database - 學校資料.csv' 和 'database - 相關文章.csv' 檔案與 app.py 在同一個資料夾中。")
        return None, None
    except Exception as e:
        st.error(f"處理資料時發生錯誤：{e}。請檢查您的 CSV 檔案格式是否正確。")
        return None, None

# --- 輔助函數 ---
def display_info(label, value):
    if pd.notna(value) and str(value).strip() and str(value).lower() not in ['nan', '-']:
        st.markdown(f"**{label}：** {str(value)}")

school_df, article_df = load_data()

# --- 主應用程式 ---
if school_df is not None and article_df is not None:
    
    # --- 篩選器介面 ---
    st.subheader("學校基本資料")
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    with row1_col1:
        regions = sorted(school_df["區域"].unique())
        selected_region = st.multiselect("區域", regions, default=[])
    with row1_col2:
        nets = sorted(school_df["小一學校網"].dropna().unique())
        selected_net = st.multiselect("小一學校網", nets, default=[])
    with row1_col3:
        cat1 = sorted(school_df["資助類型"].unique())
        selected_cat1 = st.multiselect("資助類型", cat1, default=[])

    row2_col1, row2_col2, row2_col3 = st.columns(3)
    with row2_col1:
        genders = sorted(school_df["學生性別"].unique())
        selected_gender = st.multiselect("學生性別", genders, default=[])
    with row2_col2:
        religions = sorted(school_df["宗教"].unique())
        selected_religion = st.multiselect("宗教", religions, default=[])
    with row2_col3:
        session_types = sorted(school_df["上課時間"].unique())
        selected_session = st.multiselect("上課時間", session_types, default=[])

    row3_col1, row3_col2, row3_col3 = st.columns(3)
    with row3_col1:
        languages = sorted(school_df["教學語言"].dropna().unique())
        selected_language = st.multiselect("教學語言", languages, default=[])
    with row3_col2:
        related_school_options = ["一條龍中學", "直屬中學", "聯繫中學"]
        selected_related = st.multiselect("關聯學校類型", related_school_options, default=[])
    with row3_col3:
        transport_options = ["校車", "保姆車"]
        selected_transport = st.multiselect("校車服務", transport_options, default=[])
        
    st.divider()
    st.subheader("課業安排")
    
    col_map = {
        "g1_tests": "全年全科測驗次數_一年級", "g1_exams": "全年全科考試次數_一年級",
        "g1_diverse_assessment": "小一上學期以多元化的進展性評估代替測驗及考試",
        "g2_6_tests": "全年全科測驗次數_二至六年級", "g2_6_exams": "全年全科考試次數_二至六年級",
        "tutorial_session": "按校情靈活編排時間表_盡量在下午安排導修時段_讓學生能在教師指導下完成部分家課"
    }
    
    assessment_options = ["不限", "0次", "不多於1次", "不多於2次", "3次"]
    hw_col1, hw_col2 = st.columns(2)
    with hw_col1:
        selected_g1_tests = st.selectbox("一年級測驗次數", assessment_options)
        selected_g1_exams = st.selectbox("一年級考試次數", assessment_options)
        use_diverse_assessment = st.checkbox("學校於小一上學期以多元化的進展性評估代替測驗及考試")
    with hw_col2:
        selected_g2_6_tests = st.selectbox("二至六年級測驗次數", assessment_options)
        selected_g2_6_exams = st.selectbox("二至六年級考試次數", assessment_options)
        has_tutorial_session = st.checkbox("學校盡量在下午安排導修時段讓學生能在教師指導下完成部分家課")

    if st.button("搜尋學校", type="primary", use_container_width=True):
        
        mask = pd.Series(True, index=school_df.index)
        # --- 篩選邏輯 ---
        if selected_region: mask &= school_df["區域"].isin(selected_region)
        if selected_cat1: mask &= school_df["資助類型"].isin(selected_cat1)
        if selected_gender: mask &= school_df["學生性別"].isin(selected_gender)
        if selected_session: mask &= school_df["上課時間"].isin(selected_session)
        if selected_religion: mask &= school_df["宗教"].isin(selected_religion)
        if selected_language: mask &= school_df["教學語言"].isin(selected_language)
        if selected_net: mask &= school_df["小一學校網"].isin(selected_net)
        if selected_related:
            related_mask = pd.Series(False, index=school_df.index)
            for col in selected_related:
                if col in school_df.columns: related_mask |= (school_df[col].notna() & (school_df[col] != "-"))
            mask &= related_mask
        if selected_transport:
            transport_mask = pd.Series(False, index=school_df.index)
            for col in selected_transport:
                if col in school_df.columns: transport_mask |= (school_df[col] == "有")
            mask &= transport_mask
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
        
        filtered_schools = school_df[mask]

        st.divider()
        st.subheader(f"篩選結果：共找到 {len(filtered_schools)} 間學校")
        
        if filtered_schools.empty:
            st.warning("找不到符合所有篩選條件的學校。")
        else:
            # --- 顯示方式 ---
            # 移除了原有的 "班級結構" 分類，後續會以表格形式獨立顯示
            categories = {
                "基本資料": ["區域", "小一學校網", "資助類型", "學生性別", "宗教", "上課時間", "創校年份", "校訓"],
                "聯繫方式": ["學校地址", "學校電話", "學校傳真", "學校電郵", "學校網址"],
                "管治架構": ["辦學團體", "法團校董會", "校監_校管會主席姓名", "校長姓名"],
                "學校特色": ["教學語言", "一條龍中學", "直屬中學", "聯繫中學", "校車", "保姆車"],
                "學業評估與安排": list(col_map.values()),
                "師資概況": ["上學年核准編制教師職位數目", "上學年教師總人數", "上學年已接受師資培训人數百分率", "上學年學士人數百分率", "上學年碩士_博士或以上人數百分率", "上學年特殊教育培訓人數百分率"],
                "學校設施": ["課室數目", "禮堂數目", "操場數目", "圖書館數目", "特別室", "其他學校設施", "支援有特殊教育需要學生的設施"],
                "辦學理念": ["辦學宗旨", "學校關注事項", "學校特色"],
                "費用": ["學費", "堂費", "家長教師會費", "非標準項目的核准收費", "其他收費_費用"]
            }
            categorized_cols = set(col for cols in categories.values() for col in cols)

            for index, row in filtered_schools.iterrows():
                with st.expander(f"**{row['學校名稱']}**"):
                    for category, cols in categories.items():
                        if any(pd.notna(row.get(col)) and str(row.get(col)).strip() and str(row.get(col)).lower() not in ['nan', '-'] for col in cols):
                            st.markdown(f"##### {category}")
                            if category == "辦學理念":
                                for col in cols: display_info(col, row.get(col))
                            else:
                                sub_cols = st.columns(3)
                                for i, col_name in enumerate(cols):
                                    with sub_cols[i % 3]:
                                        display_info(col_name, row.get(col_name))
                    
                    # --- 修改 START: 以表格形式顯示班級結構 ---
                    st.markdown("##### 班級結構")
                    grades = ["小一", "小二", "小三", "小四", "小五", "小六", "總"]
                    class_data = {
                        "年級": grades,
                        "上學年班數": [row.get(f"上學年{g}班數", 0) for g in grades],
                        "本學年班數": [row.get(f"本學年{g}班數", 0) for g in grades]
                    }
                    class_df = pd.DataFrame(class_data)
                    st.table(class_df.set_index('年級'))
                    # --- 修改 END ---

                    st.markdown("##### 其他資料")
                    other_cols_exist = False
                    sub_cols = st.columns(3)
                    i = 0
                    for col_name in school_df.columns:
                        if col_name not in categorized_cols and "班數" not in col_name and col_name != "學校名稱":
                            if pd.notna(row.get(col_name)) and str(row.get(col_name)).strip() and str(row.get(col_name)).lower() not in ['nan', '-']:
                                with sub_cols[i % 3]:
                                    display_info(col_name, row.get(col_name))
                                i += 1
                                other_cols_exist = True
                    if not other_cols_exist:
                        st.info("沒有其他資料可顯示。")

                    related_articles = article_df[article_df["學校名稱"] == row["學校名稱"]]
                    if not related_articles.empty:
                        st.markdown("---")
                        st.markdown("##### 相關文章")
                        for _, article_row in related_articles.iterrows():
                            title = article_row.get('文章標題')
                            link = article_row.get('文章連結')
                            if pd.notna(title) and pd.notna(link):
                                st.markdown(f"- [{title}]({link})")
