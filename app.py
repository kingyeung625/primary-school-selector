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
        # --- [START] 已更新為您的新檔名 ---
        school_df = pd.read_csv("database_school_info.csv") 
        article_df = pd.read_csv("database_related_article.csv")
        # --- [END] 更新 ---
        
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

        teacher_stat_cols = [
            "已接受師資培训人數百分率", "學士人數百分率", 
            "碩士_博士或以上人數百分率", "特殊教育培訓人數百分率",
            "0至4年年資人數百分率", "5至9年年資人數百分率", 
            "10年年資或以上人數百分率"
        ]
        
        for col in teacher_stat_cols:
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
        # --- [START] 更新錯誤訊息 ---
        st.error("錯誤：找不到資料檔案。請確保 'database_school_info.csv' 和 'database_related_article.csv' 檔案與 app.py 在同一個資料夾中。")
        # --- [END] 更新錯誤訊息 ---
        return None, None
    except Exception as e:
        st.error(f"處理資料時發生錯誤：{e}。請檢查您的 CSV 檔案格式是否正確。")
        return None, None

# --- [START] 輔助函數 (更新) ---
LABEL_MAP = { 
    "校監_校管會主席姓名": "校監", 
    "校長姓名": "校長",
    "舊生會_校友會": "舊生會／校友會", 
    "上課時間_": "一般上學時間",
    "放學時間": "一般放學時間",
    "午膳時間": "午膳開始時間",
    "午膳結束時間": "午膳結束時間",
    "上學年核准編制教師職位數目": "核准編制教師職位數目",
    "上學年教師總人數": "教師總人數",
    "上學年已接受師資培训人數百分率": "已接受師資培訓(%)",
    "上學年學士人數百分率": "學士學位(%)",
    "上學年碩士_博士或以上人數百分率": "碩士/博士學位(%)",
    "上學年特殊教育培訓人數百分率": "特殊教育培訓(%)",
    "上學年0至4年年資人數百分率": "0-4年年資(%)",
    "上學年5至9年年資人數百分率": "5-9年年資(%)",
    "上學年10年年資或以上人數百分率": "10+年年資(%)",
    "課室數目": "課室",
    "禮堂數目": "禮堂",
    "操場數目": "操場",
    "圖書館數目": "圖書館",
    "學費": "學費",
    "堂費": "堂費",
    "家長教師會費": "家長教師會費",
    "非標準項目的核准收費": "非標準項目的核准收FED",
    "其他收費_費用": "其他",
    "一條龍中學": "一條龍中學",
    "直屬中學": "直屬中學",
    "聯繫中學": "聯繫中學"
}

# 檢查資料是否有效 (不是 NaN, -, 或空字串)
def is_valid_data(value):
    return pd.notna(value) and str(value).strip() and str(value).lower() not in ['nan', '-']

# 更新 display_info 函數以始終顯示標籤
def display_info(label, value, is_fee=False):
    display_label = LABEL_MAP.get(label, label)
    display_value = "沒有" # 預設值

    if is_valid_data(value):
        # --- Value exists ---
        val_str = str(value)
        if "網頁" in label and "http" in val_str:
            st.markdown(f"**{display_label}：** [{value}]({value})")
            return 
        elif "(%)" in display_label and isinstance(value, (int, float)):
            display_value = f"{int(value)}%"
        elif is_fee:
            if isinstance(value, (int, float)) and value > 0:
                display_value = f"${int(value)}"
            elif isinstance(value, (int, float)) and value == 0:
                display_value = "$0" # 根據 DOCX 格式，費用應顯示 $0
            else:
                display_value = val_str # 用於 "N/A" 或其他文字
        else:
            display_value = val_str
    
    # 處理空的費用欄位
    elif is_fee:
        if label in ["學費", "堂費", "家長教師會費"]:
             display_value = "$0" # 數字費用預設為 $0
        else:
             display_value = "沒有" # 文字費用預設為 "沒有"
    
    # 對於非費用欄位，如果 value 無效且 label 不是 "關聯學校" (有特殊處理)，則顯示 "沒有"
    elif label == "關聯學校":
        st.markdown(f"**{display_label}：** {display_value}")
        return

    st.markdown(f"**{display_label}：** {display_value}")
# --- [END] 輔助函數 (更新) ---

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
        
        school_name_query = st.text_input(
            "根據學校名稱搜尋", 
            placeholder="請輸入學校名稱關鍵字...", 
            key="school_name_search"
        )

        with st.expander("根據學校基本資料篩選"):
            r1c1, r1c2, r1c3, r1c4 = st.columns(4)
            with r1c1: selected_region = st.multiselect("區域", sorted(school_df["區域"].unique()), key="region")
            with r1c2: selected_net = st.multiselect("小一學校網", sorted(school_df["小一學校網"].dropna().unique()), key="net")
            with r1c3: selected_cat1 = st.multiselect("資助類型", sorted(school_df["資助類型"].unique()), key="cat1")
            with r1c4: selected_gender = st.multiselect("學生性別", sorted(school_df["學生性別"].unique()), key="gender")
            
            r2c1, r2c2, r2c3, r2c4 = st.columns(4)
            with r2c1: selected_religion = st.multiselect("宗教", sorted(school_df["宗教"].unique()), key="religion")
            with r2c2: selected_language = st.multiselect("教學語言", sorted(school_df["教學語言"].dropna().unique()), key="lang")
            with r2c3: selected_related = st.multiselect("關聯學校類型", ["一條龍中學", "直屬中學", "聯繫中學"], key="related")
            with r2c4: selected_transport = st.multiselect("校車服務", ["校車", "保姆車"], key="transport")

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
        
        with st.expander("根據師資篩選"):
            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                selected_masters_pct = st.slider("碩士/博士或以上學歷 (最少%)", 0, 100, 0, key="masters_pct")
            with tc2:
                selected_exp_pct = st.slider("10年或以上年資 (最少%)", 0, 100, 0, key="exp_pct")
            with tc3:
                selected_sen_pct = st.slider("特殊教育培訓 (最少%)", 0, 100, 0, key="sen_pct")

        st.write("") 
        if st.button("🚀 搜尋學校", type="primary", use_container_width=True):
            st.session_state.search_mode = True
            
            mask = pd.Series(True, index=school_df.index)
            query = school_name_query.strip()
            if query: mask &= school_df["學校名稱"].str.contains(query, case=False, na=False)
            if selected_region: mask &= school_df["區域"].isin(selected_region)
            if selected_cat1: mask &= school_df["資助類型"].isin(selected_cat1)
            if selected_gender: mask &= school_df["學生性別"].isin(selected_gender)
            if selected_religion: mask &= school_df["宗教"].isin(selected_religion)
            if selected_language: mask &= school_df["教學語言"].isin(selected_language)
            if selected_net: mask &= school_df["小一學校網"].isin(selected_net)
            if selected_related:
                related_mask = pd.Series(False, index=school_df.index)
                for col in selected_related:
                    if col in school_df.columns: related_mask |= is_valid_data(school_df[col])
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
            
            if selected_masters_pct > 0:
                mask &= (school_df["碩士_博士或以上人數百分率"] >= selected_masters_pct)
            if selected_exp_pct > 0:
                mask &= (school_df["10年年資或以上人數百分率"] >= selected_exp_pct)
            if selected_sen_pct > 0:
                mask &= (school_df["特殊教育培訓人數百分率"] >= selected_sen_pct)

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
            # 欄位定義
            fee_cols = ["學費", "堂費", "家長教師會費", "非標準項目的核准收費", "其他收費_費用"]
            teacher_stat_cols = [
                "上學年已接受師資培训人數百分率", "上學年學士人數百分率", "上學年碩士_博士或以上人數百分率", 
                "上學年特殊教育培訓人數百分率", "上學年0至4年年資人數百分率", "上學年5至9年年資人數百分率", 
                "上學年10年年資或以上人數百分率", "上學年核准編制教師職位數目", "上學年教師總人數", 
                "教師專業培訓及發展"
            ]
            other_categories = {
                "辦學理念": ["辦學宗旨", "學校關注事項", "學校特色"],
            }
            facility_cols_counts = ["課室數目", "禮堂數目", "操場數目", "圖書館數目"]
            facility_cols_text = ["特別室", "其他學校設施", "支援有特殊教育需要學生的設施"]
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
            
            for index, row in filtered_schools.iterrows():
                with st.expander(f"**{row['學校名稱']}**"):
                    
                    related_articles = article_df[article_df["學校名稱"] == row["學校名稱"]]
                    if not related_articles.empty:
                        with st.expander("相關文章", expanded=False): 
                            for _, article_row in related_articles.iterrows():
                                title, link = article_row.get('文章標題'), article_row.get('文章連結')
                                if pd.notna(title) and pd.notna(link):
                                    with st.container(border=True):
                                        st.markdown(f"[{title}]({link})")

                    tab_list = ["基本資料", "學業評估與安排", "師資概況", "學校設施", "班級結構"]
                    
                    has_mission_data = any(is_valid_data(row.get(col)) for col in other_categories["辦學理念"])
                    if has_mission_data:
                        tab_list.append("辦學理念與補充資料")

                    tab_list.append("聯絡資料")
                    
                    tabs = st.tabs(tab_list)

                    # --- [START] TAB 1: 基本資料 (完全依照 DOCX 格式) ---
                    with tabs[0]:
                        st.subheader("學校基本資料")
                        # 佈局基於 source 2
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
                        
                        # --- [START] 關聯學校邏輯 (已修改) ---
                        with c10: 
                            related_dragon_val = row.get("一條龍中學")
                            related_feeder_val = row.get("直屬中學")
                            related_linked_val = row.get("聯繫中學")
                            
                            has_dragon = is_valid_data(related_dragon_val)
                            has_feeder = is_valid_data(related_feeder_val)
                            has_linked = is_valid_data(related_linked_val)

                            if not has_dragon and not has_feeder and not has_linked:
                                display_info("關聯學校", None) # 這將顯示 "關聯學校：沒有"
                            else:
                                st.markdown("**關聯學校：**") # 僅顯示標題
                                if has_dragon:
                                    # 使用 display_info 確保格式一致
                                    display_info("一條龍中學", related_dragon_val)
                                if has_feeder:
                                    display_info("直屬中學", related_feeder_val)
                                if has_linked:
                                    display_info("聯繫中學", related_linked_val)
                        # --- [END] 關聯學校邏輯 ---

                        c11, c12 = st.columns(2) # 新增的校長/校監行
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
                        # 佈局基於 source 4
                        c_transport1, c_transport2 = st.columns(2)
                        with c_transport1:
                            has_bus, has_van = row.get("校車") == "有", row.get("保姆車") == "有"
                            transport_status = "沒有"
                            if has_bus and has_van: transport_status = "有校車及保姆車"
                            elif has_bus: transport_status = "有校車"
                            elif has_van: transport_status = "有保姆車"
                            display_info("校車或保姆車", transport_status)
                        # c_transport2 保持空白，如 DOCX 所示
                        
                        c15, c16 = st.columns(2)
                        with c15: display_info("上課時間_", row.get("上課時間_")) # <-- 顯示 "一般上學時間"
                        with c16: display_info("放學時間", row.get("放學時間")) # <-- 顯示 "一般放學時間"

                        st.divider()
                        st.subheader("午膳安排")
                        # 佈局基於 source 6
                        c_lunch1, c_lunch2 = st.columns(2)
                        with c_lunch1: display_info("午膳安排", row.get("午膳安排"))
                        # c_lunch2 保持空白，如 DOCX 所示

                        c17, c18 = st.columns(2)
                        with c17: display_info("午膳時間", row.get("午膳時間")) # <-- 顯示 "午膳開始時間"
                        with c18: display_info("午膳結束時間", row.get("午膳結束時間"))

                        st.divider()
                        st.subheader("費用")
                        # 佈局基於 source 8 (單欄列表)
                        for col_key in fee_cols:
                            display_info(col_key, row.get(col_key), is_fee=True)
                    # --- [END] TAB 1 ---

                    # --- TAB 2: 學業評估與安排 ---
                    with tabs[1]:
                        st.subheader("學業評估與安排")
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
                        for label, col_name in assessment_display_map.items():
                            if label not in ["一年級測驗次數", "一年級考試次數", "二至六年級測驗次數", "二至六年級考試次數", "小一上學期多元化評估", "下午設導修課"]:
                                display_info(label, row.get(col_name))

                    # --- TAB 3: 師資概況 ---
                    with tabs[2]:
                        st.subheader("師資概況")
                        sub_cols = st.columns(3)
                        stat_cols_to_display = [col for col in teacher_stat_cols if col != "教師專業培訓及發展"] # 排除長文字
                        for i, col_name in enumerate(stat_cols_to_display):
                            with sub_cols[i % 3]:
                                display_info(col_name, row.get(col_name))
                        
                        st.divider()
                        display_info("教師專業培訓及發展", row.get("教師專業培訓及發展"))

                    # --- TAB 4: 學校設施 ---
                    with tabs[3]:
                        st.subheader("設施數量")
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: display_info("課室數目", row.get("課室數目"))
                        with c2: display_info("禮堂數目", row.get("禮堂數目"))
                        with c3: display_info("操場數目", row.get("操場數目"))
                        with c4: display_info("圖書館數目", row.get("圖書館數目"))
                        
                        st.divider()
                        st.subheader("設施詳情")
                        for col in facility_cols_text:
                            display_info(col, row.get(col))

                    # --- TAB 5: 班級結構 ---
                    with tabs[4]:
                        st.subheader("班級結構")
                        grades_display = ["小一", "小二", "小三", "小四", "小五", "小六", "總數"]
                        grades_internal = ["小一", "小二", "小三", "小四", "小五", "小六", "總"]
                        last_year_data = [row.get(f"上學年{g}班數", 0) for g in grades_internal]
                        this_year_data = [row.get(f"本學年{g}班數", 0) for g in grades_internal]
                        class_df = pd.DataFrame([last_year_data, this_year_data], columns=grades_display, index=["上學年班數", "本學年班數"])
                        st.table(class_df)

                    # --- 動態 TABS ---
                    tab_index = 5
                    if has_mission_data:
                        with tabs[tab_index]:
                            st.subheader("辦學理念")
                            for col in other_categories["辦學理念"]:
                                display_info(col, row.get(col))
                            
                            st.divider()
                            st.subheader("其他補充資料")
                            # 建立一個所有已被顯示的欄位 set
                            displayed_cols = set()
                            for cols_list in [fee_cols, teacher_stat_cols, other_categories["辦學理念"], facility_cols_counts, facility_cols_text, assessment_display_map.values(), ["區域", "小一學校網", "資助類型", "學生性別", "創校年份", "宗教", "教學語言", "校車", "保姆車", "辦學團體", "校訓", "校長姓名", "校長稱謂", "校監_校管會主席姓名", "校監_校管會主席稱謂", "家長教師會", "舊生會_校友會", "一條龍中學", "直屬中學", "聯繫中學", "上課時間", "上課時間_", "放學時間", "午膳安排", "午膳時間", "午膳結束時間", "學校名稱", "學校地址", "學校電話", "學校傳真", "學校電郵", "學校網址", "學校佔地面積"]]:
                                displayed_cols.update(cols_list)
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
