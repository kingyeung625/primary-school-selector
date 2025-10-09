import streamlit as st
import pandas as pd
import numpy as np

# --- 頁面設定 ---
st.set_page_config(page_title="香港小學選校篩選器", layout="wide")

# --- 主標題 ---
st.title("香港小學選校篩選器")

# --- 初始化 Session State ---
if 'search_mode' not in st.session_state:
    st.session_state.search_mode = False
if 'filtered_schools' not in st.session_state:
    st.session_state.filtered_schools = pd.DataFrame()

# --- 載入與處理資料 ---
@st.cache_data
def load_data():
    try:
        school_df = pd.read_csv("database - 學校資料.csv")
        article_df = pd.read_csv("database - 相關文章.csv")

        school_df.columns = school_df.columns.str.strip()
        article_df.columns = article_df.columns.str.strip()

        school_df.rename(columns={"學校類別1": "資助類型", "學校類別2": "上課時間"}, inplace=True)

        for col in school_df.select_dtypes(include=['object']).columns:
            if school_df[col].dtype == 'object':
                school_df[col] = school_df[col].str.replace('<br>', '\n', regex=False).str.strip()

        if '學校名稱' in school_df.columns:
            school_df['學校名稱'] = school_df['學校名稱'].str.replace(r'\s+', ' ', regex=True).str.strip()

        fee_columns = ["學費", "堂費", "家長教師會費"]
        for col in fee_columns:
            if col in school_df.columns:
                school_df[col] = pd.to_numeric(school_df[col].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce').fillna(0)

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
        st.error("錯誤：找不到資料檔案。請確保 'database - 學校資料.csv' 和 'database - 相關文章.csv' 檔案與 app.py 在同一個資料夾中。")
        return None, None
    except Exception as e:
        st.error(f"處理資料時發生錯誤：{e}。請檢查您的 CSV 檔案格式是否正確。")
        return None, None

# --- 輔助函數 ---
LABEL_MAP = {
    "校監_校管會主席姓名": "校監／校管會主席姓名",
    "校長姓名": "校長",
    "舊生會_校友會": "舊生會／校友會"
}
def display_info(label, value):
    display_label = LABEL_MAP.get(label, label)
    if pd.notna(value) and str(value).strip() and str(value).lower() not in ['nan', '-']:
        if "網頁" in label and "http" in str(value):
            st.markdown(f"**{display_label}：** [{value}]({value})")
        else:
            st.markdown(f"**{display_label}：** {str(value)}")

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
        "diverse_learning_assessment": "多元學習評估"
    }

    if not st.session_state.search_mode:
        st.subheader("根據學校名稱搜尋")
        school_name_query = st.text_input("輸入學校名稱關鍵字", key="school_name_search", label_visibility="collapsed")

        st.subheader("根據學校基本資料篩選")
        row1_col1, row1_col2, row1_col3 = st.columns(3)
        with row1_col1: selected_region = st.multiselect("區域", sorted(school_df["區域"].unique()), key="region")
        with row1_col2: selected_net = st.multiselect("小一學校網", sorted(school_df["小一學校網"].dropna().unique()), key="net")
        with row1_col3: selected_cat1 = st.multiselect("資助類型", sorted(school_df["資助類型"].unique()), key="cat1")

        row2_col1, row2_col2, row2_col3 = st.columns(3)
        with row2_col1: selected_gender = st.multiselect("學生性別", sorted(school_df["學生性別"].unique()), key="gender")
        with row2_col2: selected_religion = st.multiselect("宗教", sorted(school_df["宗教"].unique()), key="religion")
        with row2_col3: selected_session = st.multiselect("上課時間", sorted(school_df["上課時間"].unique()), key="session")

        row3_col1, row3_col2, row3_col3 = st.columns(3)
        with row3_col1: selected_language = st.multiselect("教學語言", sorted(school_df["教學語言"].dropna().unique()), key="lang")
        with row3_col2: selected_related = st.multiselect("關聯學校類型", ["一條龍中學", "直屬中學", "聯繫中學"], key="related")
        with row3_col3: selected_transport = st.multiselect("校車服務", ["校車", "保姆車"], key="transport")

        st.divider()
        st.subheader("根據課業安排篩選")
        assessment_options = ["不限", "0次", "不多於1次", "不多於2次", "3次"]
        hw_col1, hw_col2 = st.columns(2)
        with hw_col1:
            selected_g1_tests = st.selectbox("一年級測驗次數", assessment_options, key="g1_tests")
            selected_g1_exams = st.selectbox("一年級考試次數", assessment_options, key="g1_exams")
            use_diverse_assessment = st.checkbox("學校於小一上學期以多元化的進展性評估代替測驗及考試", key="diverse")
        with hw_col2:
            selected_g2_6_tests = st.selectbox("二至六年級測驗次數", assessment_options, key="g2_6_tests")
            selected_g2_6_exams = st.selectbox("二至六年級考試次數", assessment_options, key="g2_6_exams")
            has_tutorial_session = st.checkbox("學校盡量在下午安排導修時段讓學生能在教師指導下完成部分家課", key="tutorial")

        st.text("")
        if st.button("🚀 搜尋學校", type="primary", use_container_width=True):
            st.session_state.search_mode = True

            mask = pd.Series(True, index=school_df.index)
            query = school_name_query.strip()
            if query: mask &= school_df["學校名稱"].str.contains(query, case=False, na=False)
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

            st.session_state.filtered_schools = school_df[mask]
            st.rerun()

    else:
        if st.button("✏️ 返回並修改篩選條件"):
            st.session_state.search_mode = False
            st.rerun()

        st.divider()
        filtered_schools = st.session_state.filtered_schools
        st.subheader(f"篩選結果：共找到 {len(filtered_schools)} 間學校")

        if filtered_schools.empty:
            st.warning("找不到符合所有篩選條件的學校。")
        else:
            base_info_cols = [
                "區域", "小一學校網", "資助類型", "上課時間", "學生性別",
                "創校年份", "校訓", "宗教", "學校佔地面積",
                "辦學團體", "校監_校管會主席姓名", "校長姓名", "家長教師會", "舊生會_校友會",
                "上課時間_", "放學時間", "午膳時間", "午膳結束時間", "午膳安排"
            ]
            other_categories = {
                "學校特色": ["一條龍中學", "直屬中學", "聯繫中學"],
                "師資概況": [
                    "上學年核准編制教師職位數目", "上學年教師總人數",
                    "上學年已接受師資培训人數百分率", "上學年學士人數百分率",
                    "上學年碩士_博士或以上人數百分率", "上學年特殊教育培訓人數百分率",
                    "上學年0至4年年資人數百分率", "上學年5至9年年資人數百分率", "上學年10年年資或以上人數百分率",
                    "教師專業培訓及發展"
                ],
                "辦學理念": ["辦學宗旨", "學校關注事項", "學校特色"],
            }
            contact_cols = ["學校地址", "學校電話", "學校傳真", "學校電郵", "學校網址"]
            facility_cols = ["課室數目", "禮堂數目", "操場數目", "圖書館數目", "特別室", "其他學校設施", "支援有特殊教育需要學生的設施"]
            fee_cols = {"學費": "學費", "堂費": "堂費", "家長教師會費": "家長教師會費", "非標準項目的核准收費": "非標準項目的核准收費", "其他收費_費用": "其他"}
            
            # --- 修改 START: 將班級教學模式和分班安排加入
            assessment_display_map = {
                "一年級測驗次數": col_map["g1_tests"], "一年級考試次數": col_map["g1_exams"],
                "小一上學期多元化評估": col_map["g1_diverse_assessment"],
                "二至六年級測驗次數": col_map["g2_6_tests"], "二至六年級考試次數": col_map["g2_6_exams"],
                "下午設導修課": col_map["tutorial_session"],
                "多元學習評估": "多元學習評估",
                "避免長假期後測考": "避免緊接在長假期後安排測考_讓學生在假期有充分的休息",
                "網上校本課業政策": "將校本課業政策上載至學校網頁_讓公眾及持份者知悉",
                "制定校本課業政策": "制定適切的校本課業政策_讓家長了解相關安排_並定期蒐集教師_學生和家長的意見",
                "班級教學模式": "班級教學模式",
                "分班安排": "分班安排"
            }
            # --- 修改 END ---
            
            excluded_cols = set(base_info_cols)
            excluded_cols.update(col for cols in other_categories.values() for col in cols)
            excluded_cols.update(contact_cols)
            excluded_cols.update(facility_cols)
            excluded_cols.update(fee_cols.keys())
            excluded_cols.update(assessment_display_map.values())
            excluded_cols.update([
                "校車", "保姆車", "校監_校管會主席稱謂", "校長稱謂", "法團校董會",
                "校監和校董_校管會主席和成員的培訓達標率", "其他宗教",
                "每週上學日數", "一般上學時段", "一般放學時段", "法團校董會_校管會_校董會", "學校名稱",
                "學校管理超連結：", "學校關注事項超連結：", "教學規劃超連結：",
                "學生支援超連結：", "家校合作及校風超連結：", "未來發展超連結："
            ])

            for index, row in filtered_schools.iterrows():
                with st.expander(f"**{row['學校名稱']}**"):

                    related_articles = article_df[article_df["學校名稱"] == row["學校名稱"]]
                    if not related_articles.empty:
                        with st.expander("相關文章", expanded=True):
                            for _, article_row in related_articles.iterrows():
                                title, link = article_row.get('文章標題'), article_row.get('文章連結')
                                if pd.notna(title) and pd.notna(link):
                                    with st.container(border=True):
                                        st.markdown(f"[{title}]({link})")

                    with st.expander("基本資料"):
                        display_info("區域", row.get("區域"))
                        net_display = "不適用" if row.get("小一學校網") == "/" else row.get("小一學校網")
                        display_info("小一學校網", net_display)
                        display_info("資助類型", row.get("資助類型"))
                        display_info("上課時間", row.get("上課時間"))
                        display_info("學生性別", row.get("學生性別"))
                        display_info("創校年份", row.get("創校年份"))
                        display_info("校訓", row.get("校訓"))
                        display_info("宗教", row.get("宗教"))
                        
                        area = row.get("學校佔地面積")
                        if pd.notna(area) and area > 0:
                            display_info("學校佔地面積", f"約{int(area)}平方米")
                        
                        display_info("教學語言", row.get("教學語言"))
                        
                        has_bus, has_van = row.get("校車") == "有", row.get("保姆車") == "有"
                        transport_status = "沒有"
                        if has_bus and has_van: transport_status = "有校車及保姆車"
                        elif has_bus: transport_status = "有校車"
                        elif has_van: transport_status = "有保姆車"
                        display_info("校車或保姆車", transport_status)
                        
                        principal_name = str(row.get("校長姓名", "")).strip()
                        principal_title = str(row.get("校長稱謂", "")).strip()
                        display_info("校長", f"{principal_name}{principal_title}" if principal_name else None)
                        
                        supervisor_name = str(row.get("校監_校管會主席姓名", "")).strip()
                        supervisor_title = str(row.get("校監_校管會主席稱謂", "")).strip()
                        display_info("校監／校管會主席姓名", f"{supervisor_name}{supervisor_title}" if supervisor_name else None)
                        
                        display_info("辦學團體", row.get("辦學團體"))
                        display_info("家長教師會", row.get("家長教師會"))
                        display_info("舊生會／校友會", row.get("舊生會_校友會"))
                        
                        display_info("一般上學時間", row.get("一般上學時間"))
                        display_info("一般放學時間", row.get("一般放學時間"))
                        display_info("午膳開始時間", row.get("午膳開始時間"))
                        display_info("午膳結束時間", row.get("午膳結束時間"))
                        display_info("午膳安排", row.get("午膳安排"))

                    with st.expander("學校設施"):
                        facility_data = [{"設施項目": col, "內容／數量": row.get(col)} for col in facility_cols if pd.notna(row.get(col)) and str(row.get(col)).strip() not in ['nan', '-']]
                        if facility_data: st.table(pd.DataFrame(facility_data).set_index("設施項目"))
                        else: st.info("沒有學校設施資料可顯示。")
                    
                    with st.expander("學業評估與安排"):
                        # ... (顯示邏輯與前一版相同)
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            display_info("一年級測驗次數", row.get(col_map["g1_tests"]))
                            display_info("一年級考試次數", row.get(col_map["g1_exams"]))
                        with c2:
                            display_info("二至六年級測驗次數", row.get(col_map["g2_6_tests"]))
                            display_info("二至六年級考試次數", row.get(col_map["g2_6_exams"]))
                        with c3:
                            display_info("小一上學期多元化評估", row.get(col_map["g1_diverse_assessment"]))
                            display_info("下午設導修課", row.get(col_map["tutorial_session"]))
                        
                        st.divider()
                        # --- 修改 START: 加入班級教學模式和分班安排 ---
                        for label, col_name in assessment_display_map.items():
                            if label not in ["一年級測驗次數", "一年級考試次數", "二至六年級測驗次數", "二至六年級考試次數", "小一上學期多元化評估", "下午設導修課"]:
                                display_info(label, row.get(col_name))
                        # --- 修改 END ---

                    with st.expander("聯絡資料"):
                        c1, c2 = st.columns(2)
                        with c1:
                            display_info("地址", row.get("學校地址"))
                            display_info("傳真", row.get("學校傳真"))
                        with c2:
                            display_info("電話", row.get("學校電話"))
                            display_info("電郵", row.get("學校電郵"))
                        display_info("網頁", row.get("學校網址"))

                    for category, cols in other_categories.items():
                        if any(pd.notna(row.get(col)) and str(row.get(col)).strip() and str(row.get(col)).lower() not in ['nan', '-'] for col in cols):
                            with st.expander(category):
                                if category == "辦學理念":
                                    for col in cols: display_info(col, row.get(col))
                                else:
                                    sub_cols = st.columns(3)
                                    for i, col_name in enumerate(cols):
                                        with sub_cols[i % 3]:
                                            display_info(col_name, row.get(col_name))

                    with st.expander("班級結構"):
                        grades_display = ["小一", "小二", "小三", "小四", "小五", "小六", "總數"]
                        grades_internal = ["小一", "小二", "小三", "小四", "小五", "小六", "總"]
                        last_year_data = [row.get(f"上學年{g}班數", 0) for g in grades_internal]
                        this_year_data = [row.get(f"本學年{g}班數", 0) for g in grades_internal]
                        class_df = pd.DataFrame([last_year_data, this_year_data], columns=grades_display, index=["上學年班數", "本學年班數"])
                        st.table(class_df)

                    with st.expander("費用"):
                        fee_data = []
                        for col_key, col_display in fee_cols.items():
                            value = row.get(col_key)
                            display_value = "沒有"
                            if pd.notna(value):
                                if isinstance(value, (int, float)) and value > 0: display_value = f"${int(value)}"
                                elif not isinstance(value, (int, float)) and str(value).strip() not in ['-', 'nan', '0']: display_value = value
                            fee_data.append({"項目": col_display, "費用": display_value})
                        if any(item["費用"] != "沒有" for item in fee_data): st.table(pd.DataFrame(fee_data).set_index("項目"))
                        else: st.info("沒有費用資料可顯示。")

                    with st.expander("補充資料"):
                        other_cols_exist = False
                        for col_name in school_df.columns:
                            if col_name not in excluded_cols and "班數" not in col_name:
                                value = row.get(col_name)
                                if pd.notna(value) and str(value).strip() and str(value).lower() not in ['nan', '-']:
                                    display_info(col_name, value)
                                    other_cols_exist = True
                        if not other_cols_exist:
                            st.info("沒有其他補充資料可顯示。")
