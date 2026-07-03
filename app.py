import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from streamlit_calendar import calendar

st.title('筋トレ記録')

st.subheader("📅 トレーニング日を選択")

# カレンダーの設定
calendar_options = {
    "initialView": "dayGridMonth",
    "selectable": True, # 日付を選択可能にする
}

# 選択された日付を保持するメモリ（初期値は今日）
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today().strftime("%Y-%m-%d")

# 画面にカレンダーを表示して、クリックされた情報を受け取る
state = calendar(options=calendar_options, key="workout_calendar")

# もしカレンダーの日付がクリックされたら、その日付をメモリに保存する
if state and "selectInfo" in state:
    st.session_state.selected_date = state["selectInfo"]["start"][0:10]

# いま選択されている日付を取得
target_date_str = st.session_state.selected_date
st.info(f"👉 現在選択中の日付: **{target_date_str}**")

exercises = {
    '胸': ['ベンチプレス', 'ダンベルプレス', 'インクライン・ベンチプレス', 'チェストプレス', 'ペックデック / バタフライ', 'ケーブルクロスオーバー', 'ディップス', 'ダンベルフライ', 'スミスマシン・ベンチプレス', 'ダンベル・プルオーバー'],
    '腕': ['バーベルカール', 'ダンベルカール', 'プリーチャーカール', 'ケーブルカール', 'ハンマーカール', 'トライセプス・プレスダウン', 'スカルクラッシャー', 'フレンチプレス', 'キックバック', 'マシン・トライセプスエクステンション'],
    '肩': ['バーベル・ショルダープレス', 'ダンベル・ショルダープレス', 'マシン・ショルダープレス', 'サイドレイズ', 'ケーブル・サイドレイズ', 'フロントレイズ', 'リアレイズ', 'リアデルト・フライ', 'アップライトロウ', 'スミスマシン・バックプレス'],
    '背中': ['デッドリフト', 'チンニング', 'ラットプルダウン', 'ベントオーバーロウ', 'ワンアーム・ダンベルロウ', 'シーテッド・ケーブルロウ', 'Tバーロウ', 'マシンロウ', 'ケーブル・プルオーバー', 'バックエクステンション']
}
file_path = 'workout_log.csv'

st.write("---")

tab_record, tab_history = st.tabs(["✍️ 記録する", "🔍 履歴を見る"])

# ---------------------------------
# タブ1：記録する画面
# ---------------------------------
with tab_record:
    # ⚠️ 修正ポイント1：ここのインデント（字下げ）を揃えないとタブの中にフォームが入らないから直しておいたぞ！
    category = st.selectbox('部位', ['胸', '腕', '肩', '背中'])
    selected_exercise = st.selectbox('種目', exercises[category])

    st.write("---")

    # お前のこだわり設定（max_value=20）！
    num_sets = st.number_input("セット数", min_value=1, max_value=20, value=4, step=1)

    set_data = []

    with st.form(key='workout_form'):
        cols = st.columns(int(num_sets))

        for i in range(int(num_sets)):
            with cols[i]:
                st.markdown(f"**[{i+1}セット]**")
                # お前のこだわり設定（step=0.5）！
                w = st.number_input('重量(kg)', min_value=0.0, step=0.5, key=f"weight_{i}")
                r = st.number_input('回数(rep)', min_value=0, step=1, key=f"reps_{i}")

                set_data.append({"セット": i+1, "重量(kg)": w, "rep": r})
        
        st.write("---")
        submit_button = st.form_submit_button('記録する')

    if submit_button:
        save_data = []
        for row in set_data:
            save_data.append({
                "日付": target_date_str, # ⚠️ 修正ポイント2：カレンダーでタップした日付がここに入る！
                "部位": category,
                "種目": selected_exercise,
                "セット": row["セット"],
                "重量(kg)": row["重量(kg)"],
                "rep": row["rep"],
            })
        df = pd.DataFrame(save_data)

        if not os.path.exists(file_path):
            df.to_csv(file_path, mode='w', header=True, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')

        st.success(f'よし！【{category}】{selected_exercise} を {target_date_str} の記録として保存したぜ！')

# ---------------------------------
# タブ2：履歴を見る画面
# ---------------------------------
with tab_history:
    st.subheader("トレーニング記録")

    if os.path.exists(file_path):
        df_history = pd.read_csv(file_path)

        # ⚠️ 修正ポイント3：履歴も「カレンダーで選んだ日付」が自動で表示されるように連動させたぞ！
        daily_data = df_history[df_history["日付"] == target_date_str]

        if not daily_data.empty:
            st.write(f"**{target_date_str} のトレーニング内容:**")
            st.dataframe(daily_data.drop(columns=["日付"]))
        else:
            st.info(f"{target_date_str} の記録はありません")
    else:
        st.warning("記録は一つもありません")