import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from datetime import datetime,date,timedelta
from streamlit_calendar import calendar

if not st.user.is_logged_in:
    st.info("筋トレ記録アプリへようこそ！まずはログインしてくれ！")
    # ログインボタンを表示して、ここで画面の読み込みをストップさせる
    st.login("google") 
    st.stop()

# 💡 ここから下は、ログインに成功した人だけが見れる世界
# ログインしたGoogleアカウントのメールアドレスをユーザー名として使う
current_user = st.user.email 

st.sidebar.header("👤 ユーザー情報")
st.sidebar.info(f"ログイン中: {current_user}")
if st.sidebar.button("ログアウト"):
    st.logout()

# ユーザー（メアド）ごとに保存するCSVファイルを自動で分ける
file_path = f'workout_log_{current_user}.csv'

st.title('筋トレ記録')

st.subheader("📅 トレーニング日を選択")

# カレンダーの設定（セッションステートで日付を記憶）
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = str(date.today())

# カレンダーのオプション設定
calendar_options = {
    "initialView": "dayGridMonth",
    "selectable": True,
}

# カレンダーを表示し、ユーザーの操作（イベント）を受け取る
cal_result = calendar(events=[], options=calendar_options)

# カレンダーの日付がクリックされたら、記憶している日付を上書きする
if "dateClick" in cal_result:
    raw_date = str(cal_result["dateClick"]["date"])
    
    # 💡 修正ポイント2：'T'が含まれている（世界標準時）なら日本時間に変換！
    if "T" in raw_date:
        # "Z"を取り除いてPythonの日付データに変換し、9時間（日本時間分）足す
        dt_utc = datetime.fromisoformat(raw_date.replace("Z", ""))
        dt_jst = dt_utc + timedelta(hours=9)
        clicked_date = dt_jst.strftime("%Y-%m-%d") # "YYYY-MM-DD"の形に戻す
    else:
        # もし時間がついていない形式なら、そのまま使う
        clicked_date = raw_date
    
    if st.session_state.selected_date != clicked_date:
        st.session_state.selected_date = clicked_date
        st.rerun() # 日付が変わったら画面を即座に更新！

# 動作確認用：今選んでいる日付を表示
st.write(f"現在選択中の日付: {st.session_state.selected_date}")

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
    category = st.selectbox('部位', ['胸', '腕', '肩', '背中'])
    selected_exercise = st.selectbox('種目', exercises[category])

    st.write("---")

    num_sets = st.number_input("セット数", min_value=1, max_value=20, value=4, step=1)

    set_data = []

    with st.form(key='workout_form'):
        cols = st.columns(int(num_sets))

        for i in range(int(num_sets)):
            with cols[i]:
                st.markdown(f"**[{i+1}セット]**")
                # 💡 value=None を追加して、最初から空っぽの状態にする！
                w = st.number_input('重量', min_value=0.0, step=0.5, value=None, placeholder="kg", key=f"weight_{i}")
                r = st.number_input('回数', min_value=0, step=1, value=None, placeholder="rep", key=f"reps_{i}")

                set_data.append({"セット": i+1, "重量(kg)": w, "rep": r})
        
        st.write("---")
        submit_button = st.form_submit_button('記録する')

    if submit_button:
        save_data = []
        for row in set_data:
            # 💡 空欄のまま保存ボタンを押された時のエラー対策（Noneなら0として扱う）
            final_w = row["重量(kg)"] if row["重量(kg)"] is not None else 0.0
            final_r = row["rep"] if row["rep"] is not None else 0
            
            # 重量も回数も0なら、そのセットはスキップする（不要な空データを保存しない）
            if final_w == 0.0 and final_r == 0:
                continue
                
            save_data.append({
                "日付": st.session_state.selected_date,
                "部位": category,
                "種目": selected_exercise,
                "セット": row["セット"],
                "重量(kg)": final_w,
                "rep": final_r,
            })
            
        if len(save_data) > 0:
            df = pd.DataFrame(save_data)

            if not os.path.exists(file_path):
                df.to_csv(file_path, mode='w', header=True, index=False, encoding='utf-8-sig')
            else:
                df.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')

            st.success(f'よし！【{category}】{selected_exercise} を {st.session_state.selected_date} の記録として保存したぜ！')
        else:
            st.warning('入力されたデータがなかったから保存をキャンセルしたぞ！')
            # ---------------------------------
# タブ2：履歴を見る画面
# ---------------------------------
with tab_history:
    st.subheader("トレーニング記録")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        df_history = pd.read_csv(file_path)
        daily_data = df_history[df_history["日付"] == st.session_state.selected_date]

        if not daily_data.empty:
            st.write(f"**{st.session_state.selected_date} のトレーニング内容:**")
            
            for exercise_name, group_df in daily_data.groupby('種目'):
                st.markdown(f"### 🏋️ {exercise_name}")
                
                edit_exercise = st.toggle("この種目を編集・セット追加", key=f"toggle_{exercise_name}")
                
                if edit_exercise:
                    # 💡 column_config を追加して、スマホに「これは数字だ（テンキーを出せ）」と指示する！
                    edited_group_df = st.data_editor(
                        group_df[['セット', '重量(kg)', 'rep']],
                        num_rows="dynamic",
                        key=f"editor_{exercise_name}",
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "重量(kg)": st.column_config.NumberColumn(
                                "重量(kg)",
                                min_value=0.0,
                                step=0.5,
                                format="%.1f"
                            ),
                            "rep": st.column_config.NumberColumn(
                                "rep",
                                min_value=0,
                                step=1,
                                format="%d"
                            )
                        }
                    )
                    
                    if st.button(f"💾 {exercise_name} の変更を保存", key=f"save_{exercise_name}"):
                        edited_group_df['日付'] = st.session_state.selected_date
                        edited_group_df['部位'] = group_df['部位'].iloc[0]
                        edited_group_df['種目'] = exercise_name
                        
                        df_history_kept = df_history[~((df_history["日付"] == st.session_state.selected_date) & (df_history["種目"] == exercise_name))]
                        updated_df = pd.concat([df_history_kept, edited_group_df], ignore_index=True)
                        
                        updated_df.to_csv(file_path, index=False, encoding='utf-8-sig')
                        st.success(f"よし！{exercise_name} の記録を更新したぜ！")
                        st.rerun()
                
                else:
                    display_df = group_df[['セット', '重量(kg)', 'rep']]
                    st.dataframe(display_df, hide_index=True, use_container_width=True)
                    st.write("")
        else:
            st.info(f"{st.session_state.selected_date} の記録はないぜ！")
    else:
        st.warning("まだ記録が一つもないみたいだ。さっそく記録してみよう！")