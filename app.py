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

        return school_df, article_df
        
    except FileNotFoundError:
        st.error("錯誤：找不到資料檔案。請確保 'database - 學校資料.csv' 和 'database - 相關文章.csv' 檔案與 app.py 在同一個資料夾中。")
        return None, None
    except Exception as e:
        st.error(f"處理資料時發生錯誤：{e}。請檢查您的 CSV 檔案格式是否正確。")
        return None, None

school_df, article_df = load_data()

# --- 主應用程式 ---
if school_df is not None and article_df is not None:
    
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
        "g1_tests": "全年全科測驗次數_一年級",
        "g1_exams": "全年全科考試次數_一年級",
        "g1_diverse_assessment": "小一上學期以多元化的進展性評估代替測驗及考試",
        "g2_6_tests": "全年全科測驗次數_二至六年級",
        "g2_6_exams": "全年全科考試次數_二至六年級",
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
        # 篩選邏輯... (此處省略未變動的程式碼)
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
                if col in school_df.columns:
                    related_mask |= (school_df[col].notna() & (school_df[col] != "-"))
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
            # --- 修改 START: 全新的卡片式顯示方式 ---
            for index, row in filtered_schools.iterrows():
                # 每個學校都是一個可展開的容器
                with st.expander(f"**{row['學校名稱']}** ({row['區域']})"):
                    
                    # 內部使用分欄來排版
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("##### **學校資料**")
                        st.markdown(f"**地址：** {row.get('學校地址', 'N/A')}")
                        st.markdown(f"**小一學校網：** {row.get('小一學校網', 'N/A')}")
                        st.markdown(f"**資助類型：** {row.get('資助類型', 'N/A')}")
                        st.markdown(f"**學生性別：** {row.get('學生性別', 'N/A')}")
                        st.markdown(f"**宗教：** {row.get('宗教', 'N/A')}")
                        
                    with col2:
                        st.markdown("##### **聯繫方式**")
                        st.markdown(f"**電話：** {row.get('學校電話', 'N/A')}")
                        st.markdown(f"**傳真：** {row.get('學校傳真', 'N/A')}")
                        if pd.notna(row.get('學校網址')):
                            st.markdown(f"**學校網址：** [{row.get('學校網址')}]({row.get('學校網址')})")

                    st.markdown("---")
                    
                    # 顯示其他重要資訊
                    st.markdown("##### **學業評估**")
                    st.text(f"一年級測驗及考試次數：{row.get(col_map['g1_tests'], 0)}測 / {row.get(col_map['g1_exams'], 0)}考")
                    st.text(f"二至六年級測驗及考試次數：{row.get(col_map['g2_6_tests'], 0)}測 / {row.get(col_map['g2_6_exams'], 0)}考")

                    # 整合相關文章
                    related_articles = article_df[article_df["學校名稱"] == row["學校名稱"]]
                    if not related_articles.empty:
                        st.markdown("##### **相關文章**")
                        for _, article_row in related_articles.iterrows():
                            # 確保文章標題和連結存在
                            title = article_row.get('文章標題')
                            link = article_row.get('文章連結')
                            if pd.notna(title) and pd.notna(link):
                                st.markdown(f"- [{title}]({link})")
            # --- 修改 END ---
