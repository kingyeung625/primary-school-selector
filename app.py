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
        
        # --- 資料清理與預處理 ---
        # 1. 重新命名欄位
        school_df.rename(columns={
            "學校類別1": "資助類型",
            "學校類別2": "上課時間"
        }, inplace=True)

        # 2. 處理費用欄位：轉換為數字，無法轉換的設為0
        fee_columns = ["學費", "堂費"]
        for col in fee_columns:
            if col in school_df.columns:
                school_df[col] = pd.to_numeric(school_df[col].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce').fillna(0)

        # 3. 建立布林值欄位以便篩選
        # 關聯學校：檢查相關欄位是否有內容
        related_cols = ["一條龍中學", "直屬中學", "聯繫中學"]
        school_df["有關聯學校"] = school_df[related_cols].notna().any(axis=1)
        
        # 校車/保姆車：檢查相關欄位是否為 "有"
        transport_cols = ["校車", "保姆車"]
        school_df["有校車服務"] = (school_df[transport_cols] == "有").any(axis=1)
        
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
    st.subheader("篩選條件")

    # --- 使用四欄來放置所有篩選器 ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        regions = sorted(school_df["區域"].unique())
        selected_region = st.multiselect("區域", regions, default=[])
        
        cat1 = sorted(school_df["資助類型"].unique())
        selected_cat1 = st.multiselect("資助類型", cat1, default=[])

    with col2:
        genders = sorted(school_df["學生性別"].unique())
        selected_gender = st.multiselect("學生性別", genders, default=[])
        
        session_types = sorted(school_df["上課時間"].unique())
        selected_session = st.multiselect("上課時間", session_types, default=[])
        
    with col3:
        religions = sorted(school_df["宗教"].unique())
        selected_religion = st.multiselect("宗教", religions, default=[])
        
        languages = sorted(school_df["教學語言"].dropna().unique())
        selected_language = st.multiselect("教學語言", languages, default=[])

    with col4:
        # 學費滑桿
        min_fee, max_fee = int(school_df["學費"].min()), int(school_df["學費"].max())
        selected_fee = st.slider("學費範圍", min_fee, max_fee, (min_fee, max_fee))
        
        # 堂費滑桿
        min_tfee, max_tfee = int(school_df["堂費"].min()), int(school_df["堂費"].max())
        selected_tfee = st.slider("堂費範圍", min_tfee, max_tfee, (min_tfee, max_tfee))

        # 布林值篩選
        has_related_school = st.checkbox("只顯示有關聯學校")
        has_school_bus = st.checkbox("只顯示有校車或保姆車")


    # --- "搜尋學校" 按鈕 ---
    if st.button("搜尋學校", type="primary", use_container_width=True):
        
        # --- 篩選邏輯 ---
        # 建立一個布林值的 "遮罩 (mask)"，初始為全 True
        mask = pd.Series(True, index=school_df.index)

        if selected_region:
            mask &= school_df["區域"].isin(selected_region)
        if selected_cat1:
            mask &= school_df["資助類型"].isin(selected_cat1)
        if selected_gender:
            mask &= school_df["學生性別"].isin(selected_gender)
        if selected_session:
            mask &= school_df["上課時間"].isin(selected_session)
        if selected_religion:
            mask &= school_df["宗教"].isin(selected_religion)
        if selected_language:
            mask &= school_df["教學語言"].isin(selected_language)
        
        # 範圍篩選
        mask &= school_df["學費"].between(selected_fee[0], selected_fee[1])
        mask &= school_df["堂費"].between(selected_tfee[0], selected_tfee[1])

        # 布林值篩選
        if has_related_school:
            mask &= school_df["有關聯學校"]
        if has_school_bus:
            mask &= school_df["有校車服務"]

        filtered_schools = school_df[mask]

        st.divider()
        st.subheader("篩選結果")
        
        if filtered_schools.empty:
            st.warning("找不到符合所有篩選條件的學校。")
        else:
            # 隱藏我們自己建立的欄位，讓表格更乾淨
            display_cols = [col for col in school_df.columns if col not in ["有關聯學校", "有校車服務"]]
            st.dataframe(filtered_schools[display_cols])

            st.divider()

            # --- 顯示相關文章 ---
            st.subheader("相關文章")
            selected_school_name = st.selectbox("從上方篩選結果中，選擇一所學校查看相關文章", filtered_schools["學校名稱"].unique())

            if selected_school_name:
                related_articles = article_df[article_df["學校名稱"] == selected_school_name]
                if not related_articles.empty:
                    for _, row in related_articles.iterrows():
                        st.markdown(f"[{row['文章標題']}]({row['文章連結']})")
                else:
                    st.write("暫無此學校的相關文章。")
