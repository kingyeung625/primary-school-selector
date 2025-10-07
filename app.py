import streamlit as st
import pandas as pd

# 設定頁面標題和版面
st.set_page_config(page_title="香港小學選校篩選器", layout="wide")

# 主標題
st.title("香港小學選校篩選器")

# --- 載入資料 ---
@st.cache_data
def load_data():
    try:
        # 使用 "database - 學校資料.csv" 和 "database - 相關文章.csv"
        school_df = pd.read_csv("database - 學校資料.csv")
        article_df = pd.read_csv("database - 相關文章.csv")
        
        # 重新命名欄位以增加程式碼的可讀性和彈性
        school_df.rename(columns={
            "學校類別1": "資助類型",
            "學校類別2": "上課時間"
        }, inplace=True)
        
        return school_df, article_df
    except FileNotFoundError:
        st.error("錯誤：找不到資料檔案。請確保 'database - 學校資料.csv' 和 'database - 相關文章.csv' 檔案與 app.py 在同一個資料夾中。")
        return None, None
    except KeyError as e:
        st.error(f"錯誤：在資料表中找不到預期的欄位：{e}。請檢查您的 CSV 檔案是否包含正確的欄位名稱（例如 '學校類別1', '學校類別2' 等）。")
        return None, None

school_df, article_df = load_data()

# --- 主應用程式 ---
if school_df is not None and article_df is not None:
    st.subheader("篩選條件")

    # --- 將篩選器移至主頁面，並使用分欄排版 ---
    col1, col2, col3 = st.columns(3)

    with col1:
        # 區域篩選
        regions = sorted(school_df["區域"].unique())
        selected_region = st.multiselect("區域", regions, default=regions)
        
        # 資助類型 篩選 (原 學校類別1)
        cat1 = sorted(school_df["資助類型"].unique())
        selected_cat1 = st.multiselect("資助類型", cat1, default=cat1)

    with col2:
        # 學生性別 篩選
        genders = sorted(school_df["學生性別"].unique())
        selected_gender = st.multiselect("學生性別", genders, default=genders)
        
        # 上課時間 篩選 (原 學校類別2)
        session_types = sorted(school_df["上課時間"].unique())
        selected_session = st.multiselect("上課時間", session_types, default=session_types)

    with col3:
        # 宗教 篩選
        religions = sorted(school_df["宗教"].unique())
        selected_religion = st.multiselect("宗教", religions, default=religions)

    # 分隔線
    st.divider()

    # --- 篩選邏輯 ---
    filtered_schools = school_df[
        (school_df["區域"].isin(selected_region)) &
        (school_df["資助類型"].isin(selected_cat1)) &
        (school_df["上課時間"].isin(selected_session)) &
        (school_df["學生性別"].isin(selected_gender)) &
        (school_df["宗教"].isin(selected_religion))
    ]

    # --- 顯示結果 ---
    st.subheader("篩選結果")
    st.dataframe(filtered_schools)

    st.divider()

    # --- 顯示相關文章 ---
    st.subheader("相關文章")
    if not filtered_schools.empty:
        # 使用下拉選單選擇學校
        selected_school_name = st.selectbox("從上方篩選結果中，選擇一所學校查看相關文章", filtered_schools["學校名稱"].unique())

        if selected_school_name:
            related_articles = article_df[article_df["學校名稱"] == selected_school_name]
            if not related_articles.empty:
                for index, row in related_articles.iterrows():
                    st.markdown(f"[{row['文章標題']}]({row['文章連結']})")
            else:
                st.write("暫無此學校的相關文章。")
    else:
        st.warning("沒有符合篩選條件的學校。")
