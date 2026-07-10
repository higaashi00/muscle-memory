import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, date
from datetime import datetime,date,timedelta
from streamlit_calendar import calendar
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

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
    '背中': ['デッドリフト', 'チンニング', 'ラットプルダウン', 'ベントオーバーロウ', 'ワンアーム・ダンベルロウ', 'シーテッド・ケーブルロウ', 'Tバーロウ', 'マシンロウ', 'ケーブル・プルオーバー', 'バックエクステンション'],
    '脚': ['スクワット', 'レッグプレス', 'レッグエクステンション', 'レッグカール', 'ランジ', 'カーフレイズ', 'ブルガリアンスクワット', 'スミスマシン・スクワット', 'ハックスクワット', 'フロントスクワット'],
    'お尻': ['ヒップスラスト', 'グルートブリッジ', 'ケーブル・キックバック', 'マシン・ヒップアブダクション', 'ワイドスクワット', 'ドンキーキック', 'ケーブル・プルスルー', 'ルーマニアン・デッドリフト', 'リバース・ハイパーエクステンション', 'スミスマシン・ヒップスラスト'],
    '腹筋': ['クランチ', 'シットアップ', 'レッグレイズ', 'アブローラー', 'プランク', 'ケーブルクランチ', 'ロシアンツイスト', 'ハンギング・レッグレイズ', 'Vシット', 'バイシクルクランチ'],
    '有酸素': ['トレッドミル', 'エアロバイク', 'クロストレーナー', 'エルゴメーター', 'ウォーキング', 'スイミング', 'ランニング']
}
file_path = 'workout_log.csv'

# 種目データを管理するJSONファイルのパス
exercises_file = f'exercises_{current_user}.json'

# 種目データを読み込み、ないなら初期化する
def load_exercises():
    if os.path.exists(exercises_file):
        with open(exercises_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return exercises

# 種目データを保存する
def save_exercises(data):
    with open(exercises_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== 基本情報管理 ====================

# 基本情報ファイルのパス
user_info_file = f'user_info_{current_user}.json'

# デフォルト基本情報
DEFAULT_USER_INFO = {
    'weight': 70.0,
    'height': 170,
    'age': 30,
    'gender': '男性'
}

# 基本情報を読み込み
def load_user_info():
    if os.path.exists(user_info_file):
        with open(user_info_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return DEFAULT_USER_INFO.copy()

# 基本情報を保存
def save_user_info(data):
    with open(user_info_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# セッションステートに基本情報を保存
if 'user_info' not in st.session_state:
    st.session_state.user_info = load_user_info()

# セッションステートに種目データを保存
if 'exercises' not in st.session_state:
    st.session_state.exercises = load_exercises()

# ==================== メッツ値定義 ====================

METS_VALUES = {
    'ベンチプレス': 6.0,
    'ダンベルプレス': 6.0,
    'インクライン・ベンチプレス': 6.0,
    'チェストプレス': 6.0,
    'ペックデック / バタフライ': 5.0,
    'ケーブルクロスオーバー': 5.0,
    'ディップス': 7.0,
    'ダンベルフライ': 5.5,
    'スミスマシン・ベンチプレス': 6.0,
    'ダンベル・プルオーバー': 5.5,
    'バーベルカール': 5.0,
    'ダンベルカール': 5.0,
    'プリーチャーカール': 5.0,
    'ケーブルカール': 5.0,
    'ハンマーカール': 5.0,
    'トライセプス・プレスダウン': 5.0,
    'スカルクラッシャー': 5.0,
    'フレンチプレス': 5.0,
    'キックバック': 5.0,
    'マシン・トライセプスエクステンション': 5.0,
    'バーベル・ショルダープレス': 6.5,
    'ダンベル・ショルダープレス': 6.5,
    'マシン・ショルダープレス': 6.0,
    'サイドレイズ': 4.0,
    'ケーブル・サイドレイズ': 4.0,
    'フロントレイズ': 4.0,
    'リアレイズ': 4.0,
    'リアデルト・フライ': 4.5,
    'アップライトロウ': 5.5,
    'スミスマシン・バックプレス': 6.5,
    'デッドリフト': 9.0,
    'チンニング': 8.0,
    'ラットプルダウン': 6.0,
    'ベントオーバーロウ': 7.0,
    'ワンアーム・ダンベルロウ': 7.0,
    'シーテッド・ケーブルロウ': 6.0,
    'Tバーロウ': 7.0,
    'マシンロウ': 6.0,
    'ケーブル・プルオーバー': 5.5,
    'バックエクステンション': 5.5,
    'スクワット': 8.0,
    'レッグプレス': 7.0,
    'レッグエクステンション': 5.5,
    'レッグカール': 5.5,
    'ランジ': 7.0,
    'カーフレイズ': 5.0,
    'ブルガリアンスクワット': 7.5,
    'スミスマシン・スクワット': 8.0,
    'ハックスクワット': 7.5,
    'フロントスクワット': 8.5,
    'ヒップスラスト': 6.5,
    'グルートブリッジ': 5.5,
    'ケーブル・キックバック': 5.0,
    'マシン・ヒップアブダクション': 4.5,
    'ワイドスクワット': 7.5,
    'ドンキーキック': 5.0,
    'ケーブル・プルスルー': 6.0,
    'ルーマニアン・デッドリフト': 8.0,
    'リバース・ハイパーエクステンション': 6.0,
    'スミスマシン・ヒップスラスト': 6.5,
    'クランチ': 4.0,
    'シットアップ': 4.5,
    'レッグレイズ': 5.0,
    'アブローラー': 6.0,
    'プランク': 4.0,
    'ケーブルクランチ': 4.5,
    'ロシアンツイスト': 4.0,
    'ハンギング・レッグレイズ': 7.0,
    'Vシット': 7.0,
    'バイシクルクランチ': 4.5,
    'トレッドミル': 7.0,
    'エアロバイク': 6.0,
    'クロストレーナー': 7.0,
    'エルゴメーター': 6.0,
    'ウォーキング': 3.5,
    'スイミング': 8.0,
    'ランニング': 9.0
}

# 部位別の消費カロリー係数（大きな筋肉ほど多く消費）
MUSCLE_SIZE_FACTOR = {
    '胸': 1.1,
    '腕': 0.8,
    '肩': 1.0,
    '背中': 1.4,
    '脚': 1.5,
    'お尻': 1.3,
    '腹筋': 0.7,
    '有酸素': 1.0
}

# ==================== 消費カロリー計算関数 ====================

def calculate_calories(weight, mets, sets, reps, gender='男性', muscle_factor=1.0):
    """
    消費カロリーを計算
    - 1回の動作 ≈ 3秒と仮定
    - 性別による係数調整：女性は0.85倍
    - 部位による係数調整：大きな筋肉ほど多く消費
    """
    # 平均回数を計算（repsはリスト）
    if isinstance(reps, list):
        valid_reps = [r for r in reps if r and r > 0]
        avg_reps = sum(valid_reps) / len(valid_reps) if valid_reps else 0
    else:
        avg_reps = reps if reps and reps > 0 else 0
    
    # 実運動時間を計算（1回3秒）
    total_reps = sets * avg_reps
    time_in_minutes = (total_reps * 3) / 60
    time_in_hours = time_in_minutes / 60
    
    # 基本カロリー計算
    calories = mets * weight * time_in_hours
    
    # 性別による係数調整
    gender_factor = 0.85 if gender == '女性' else 1.0
    calories = calories * gender_factor
    
    # 筋肉の大きさによる係数調整
    calories = calories * muscle_factor
    
    return calories

def get_daily_calories(file_path, user_weight, gender='男性'):
    """今日の消費カロリー合計を計算"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return 0.0
    
    df = pd.read_csv(file_path)
    df['日付'] = pd.to_datetime(df['日付'])
    
    today = date.today()
    today_df = df[df['日付'].dt.date == today]
    
    total_calories = 0.0
    for _, row in today_df.iterrows():
        mets = METS_VALUES.get(row['種目'], 5.0)
        muscle_factor = MUSCLE_SIZE_FACTOR.get(row['部位'], 1.0)
        exercise_calories = calculate_calories(user_weight, mets, row['セット'], row['rep'], gender, muscle_factor)
        total_calories += exercise_calories
    
    return total_calories

def get_monthly_calories(file_path, user_weight, gender='男性'):
    """今月の消費カロリー合計を計算"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return 0.0
    
    df = pd.read_csv(file_path)
    df['日付'] = pd.to_datetime(df['日付'])
    
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    
    monthly_df = df[(df['日付'].dt.date >= first_day_of_month) & (df['日付'].dt.date <= today)]
    
    total_calories = 0.0
    for _, row in monthly_df.iterrows():
        mets = METS_VALUES.get(row['種目'], 5.0)
        muscle_factor = MUSCLE_SIZE_FACTOR.get(row['部位'], 1.0)
        exercise_calories = calculate_calories(user_weight, mets, row['セット'], row['rep'], gender, muscle_factor)
        total_calories += exercise_calories
    
    return total_calories

# ==================== 統計情報用ヘルパー関数 ====================

def get_consecutive_training_days(file_path):
    """連続トレーニング日数を計算"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return 0
    
    df = pd.read_csv(file_path)
    df['日付'] = pd.to_datetime(df['日付'])
    
    # トレーニング日のみを抽出（重複を削除）
    training_dates = sorted(df['日付'].dt.date.unique(), reverse=True)
    
    if not training_dates:
        return 0
    
    # 今日がトレーニングしたか確認
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    consecutive_days = 0
    current_check_date = today
    
    for training_date in training_dates:
        if training_date == current_check_date or training_date == current_check_date - timedelta(days=consecutive_days):
            consecutive_days += 1
            current_check_date = training_date
        else:
            break
    
    return consecutive_days

def get_monthly_training_count(file_path):
    """今月のトレーニング日数を計算"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return 0
    
    df = pd.read_csv(file_path)
    df['日付'] = pd.to_datetime(df['日付'])
    
    # 今月の日付を取得
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    
    # 今月のトレーニング日のみを抽出（ユニークな日付）
    monthly_df = df[(df['日付'].dt.date >= first_day_of_month) & (df['日付'].dt.date <= today)]
    training_count = len(monthly_df['日付'].dt.date.unique())
    
    return training_count

def generate_share_text(consecutive_days, monthly_count, today_date):
    """SNS共有用のテキストを生成"""
    text = f"🏋️ 筋トレ継続{consecutive_days}日目\n"
    text += f"📅 今月{monthly_count}回目のトレーニング\n"
    text += f"📍 {today_date}\n"
    text += f"\n#筋トレ #続ける力 #フィットネス"
    return text

def create_training_chart(file_path):
    """月間トレーニング回数の折れ線グラフを作成"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        st.warning("記録がないためグラフを表示できません")
        return None
    
    df = pd.read_csv(file_path)
    df['日付'] = pd.to_datetime(df['日付'])
    
    # 日ごとのトレーニング有無をカウント
    daily_training = df.groupby(df['日付'].dt.date)['日付'].count()
    daily_training.index = pd.to_datetime(daily_training.index)
    
    # グラフを作成
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_training.index, daily_training.values, marker='o', linewidth=2, markersize=6, color='#FF6B6B')
    ax.fill_between(daily_training.index, daily_training.values, alpha=0.3, color='#FF6B6B')
    
    ax.set_xlabel('日付', fontsize=12, fontproperties='MS Gothic')
    ax.set_ylabel('トレーニング回数', fontsize=12, fontproperties='MS Gothic')
    ax.set_title('トレーニング記録', fontsize=14, fontproperties='MS Gothic', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # x軸のフォーマット
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig

st.write("---")

tab_record, tab_history, tab_stats, tab_profile = st.tabs(["✍️ 記録する", "🔍 履歴を見る", "📊 統計", "⚙️ 基本情報"])

# ---------------------------------
# タブ1：記録する画面
# ---------------------------------
with tab_record:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        category = st.selectbox('部位', list(st.session_state.exercises.keys()))
    
    with col2:
        if st.button('➕ 新しい部位を追加'):
            st.session_state.show_new_category = True
    
    # 新しい部位を追加するフォーム
    if st.session_state.get('show_new_category', False):
        new_category = st.text_input('新しい部位の名前を入力', key='new_category_input')
        col_add, col_cancel = st.columns(2)
        
        with col_add:
            if st.button('追加'):
                if new_category and new_category not in st.session_state.exercises:
                    st.session_state.exercises[new_category] = []
                    save_exercises(st.session_state.exercises)
                    st.session_state.show_new_category = False
                    st.success(f'✅ 部位「{new_category}」を追加しました！')
                    st.rerun()
                elif new_category in st.session_state.exercises:
                    st.warning('その部位はもう存在します')
                else:
                    st.warning('部位の名前を入力してください')
        
        with col_cancel:
            if st.button('キャンセル'):
                st.session_state.show_new_category = False
                st.rerun()
    
    st.write("---")
    
    # 種目の選択
    exercise_options = st.session_state.exercises.get(category, [])
    exercise_options_with_new = exercise_options + ['➕ 新しい種目を追加']
    
    selected_option = st.selectbox('種目', exercise_options_with_new, key='exercise_select')
    
    # 新しい種目を追加する場合
    if selected_option == '➕ 新しい種目を追加':
        new_exercise = st.text_input(
            f'「{category}」に追加する新しい種目の名前',
            placeholder='例：バーベルカール',
            key='new_exercise_input'
        )
        
        col_add, col_cancel = st.columns(2)
        
        with col_add:
            if st.button('新しい種目を追加する'):
                if new_exercise and new_exercise not in st.session_state.exercises[category]:
                    st.session_state.exercises[category].append(new_exercise)
                    st.session_state.exercises[category].sort()  # アルファベット順でソート
                    save_exercises(st.session_state.exercises)
                    st.success(f'✅ 種目「{new_exercise}」を「{category}」に追加しました！')
                    st.rerun()
                elif new_exercise in st.session_state.exercises[category]:
                    st.warning('その種目はもう存在します')
                else:
                    st.warning('種目の名前を入力してください')
        
        with col_cancel:
            if st.button('キャンセル'):
                st.rerun()
        
        selected_exercise = None
    else:
        selected_exercise = selected_option

    st.write("---")

    if selected_exercise is not None:
        # 前回の記録を取得して表示
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            df_history = pd.read_csv(file_path)
            # 同じ部位と種目で絞り込み
            matching_records = df_history[(df_history["部位"] == category) & (df_history["種目"] == selected_exercise)]
            
            if not matching_records.empty:
                # 最新の記録を取得（日付で逆順ソート）
                latest_record = matching_records.sort_values("日付", ascending=False).iloc[0]
                
                st.info(f"📋 前回の記録: 【{latest_record['日付']}】")
                
                # 前回の記録の詳細を表示
                prev_sets = matching_records[matching_records["日付"] == latest_record["日付"]]
                prev_df = prev_sets[['セット', '重量(kg)', 'rep']].copy()
                st.dataframe(prev_df, hide_index=True, use_container_width=True)
                st.write("")
        
        st.write("---")
        
        # セット入力管理用セッションステート
        if 'set_records' not in st.session_state:
            st.session_state.set_records = []
        
        # 次のセット番号
        next_set_number = len(st.session_state.set_records) + 1
        
        # 現在のセット入力フォーム
        st.markdown(f"### 🏋️ {selected_exercise} - Set {next_set_number}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input(
                "重量",
                min_value=0.0,
                step=0.5,
                value=None,
                placeholder="kg",
                key=f"weight_input_{next_set_number}"
            )
        
        with col2:
            reps = st.number_input(
                "回数",
                min_value=0,
                step=1,
                value=None,
                placeholder="reps",
                key=f"reps_input_{next_set_number}"
            )
        
        st.write("")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button(f"✅ セット {next_set_number} 完了", use_container_width=True, key=f"complete_{next_set_number}"):
                if weight is not None and weight > 0 and reps is not None and reps > 0:
                    # セット記録を追加
                    st.session_state.set_records.append({
                        "セット": next_set_number,
                        "重量(kg)": weight,
                        "rep": reps
                    })
                    st.rerun()
                else:
                    st.warning("重量と回数を入力してください")
        
        with col2:
            if st.button("➕ 新規セット", use_container_width=True, key="skip_to_next"):
                # 入力を飛ばして次のセットへ
                st.session_state.set_records.append({
                    "セット": next_set_number,
                    "重量(kg)": weight if (weight is not None and weight > 0) else 0,
                    "rep": reps if (reps is not None and reps > 0) else 0
                })
                st.rerun()
        
        with col3:
            if st.button("🗑️ リセット", use_container_width=True, key="reset_all"):
                st.session_state.set_records = []
                st.rerun()
        
        # 既に記録済みのセットを表示
        if st.session_state.set_records:
            st.write("---")
            st.markdown("#### 📋 記録済みセット")
            for record in st.session_state.set_records:
                st.markdown(f"**S{record['セット']}** - {record['重量(kg)']} kg × {record['rep']} reps ✓")
            
            st.write("")
            
            # 記録を保存するボタン
            if st.button("💾 トレーニング記録を保存する", use_container_width=True, key="save_all"):
                save_data = []
                for row in st.session_state.set_records:
                    final_w = row["重量(kg)"] if row["重量(kg)"] is not None else 0.0
                    final_r = row["rep"] if row["rep"] is not None else 0
                    
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
                    
                    # リセット
                    st.session_state.set_records = []
                    
                    st.rerun()
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

# ---------------------------------
# タブ3：統計・SNS共有画面
# ---------------------------------
with tab_stats:
    st.subheader("📊 トレーニング統計")
    
    # 統計情報を計算
    consecutive_days = get_consecutive_training_days(file_path)
    monthly_count = get_monthly_training_count(file_path)
    today_date = date.today().strftime("%Y年%m月%d日")
    
    # ユーザーの体重と性別を取得
    user_weight = st.session_state.user_info.get('weight', 70.0)
    user_gender = st.session_state.user_info.get('gender', '男性')
    
    # 統計情報を表示（メトリクスで視覚的に）
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔥 継続日数", f"{consecutive_days}日")
    
    with col2:
        st.metric("📅 今月のトレーニング日数", f"{monthly_count}日")
    
    with col3:
        daily_calories = get_daily_calories(file_path, user_weight, user_gender)
        st.metric("🔥 今日の消費カロリー", f"{daily_calories:.0f} kcal")
    
    st.write("---")
    
    # 今月の消費カロリー
    monthly_calories = get_monthly_calories(file_path, user_weight, user_gender)
    st.metric("📅 今月の消費カロリー合計", f"{monthly_calories:.0f} kcal")
    
    st.write("---")
    
    # グラフ表示セクション
    st.subheader("📈 トレーニング記録グラフ")
    
    fig = create_training_chart(file_path)
    
    if fig is not None:
        st.pyplot(fig)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 グラフを画像として保存", use_container_width=True):
                img_filename = f'training_chart_{current_user.replace("@", "_").replace(".", "_")}.png'
                fig.savefig(img_filename, dpi=150, bbox_inches='tight')
                st.success(f"✅ グラフを保存しました: {img_filename}")
        
        with col2:
            if st.button("🗑️ グラフをリセット", use_container_width=True):
                st.rerun()

# ---------------------------------
# タブ4：基本情報設定画面
# ---------------------------------
with tab_profile:
    st.subheader("⚙️ 基本情報設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        weight = st.number_input(
            "体重 (kg)",
            min_value=30.0,
            max_value=200.0,
            value=float(st.session_state.user_info.get('weight', 70.0)),
            step=0.5
        )
    
    with col2:
        height = st.number_input(
            "身長 (cm)",
            min_value=140,
            max_value=220,
            value=int(st.session_state.user_info.get('height', 170)),
            step=1
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        age = st.number_input(
            "年齢 (歳)",
            min_value=15,
            max_value=100,
            value=int(st.session_state.user_info.get('age', 30)),
            step=1
        )
    
    with col4:
        gender = st.selectbox(
            "性別",
            ['男性', '女性'],
            index=0 if st.session_state.user_info.get('gender') == '男性' else 1
        )
    
    # BMI計算
    bmi = weight / ((height / 100) ** 2)
    st.metric("BMI", f"{bmi:.1f}")
    
    st.write("---")
    
    if st.button("💾 基本情報を保存", use_container_width=True):
        st.session_state.user_info = {
            'weight': weight,
            'height': height,
            'age': age,
            'gender': gender
        }
        save_user_info(st.session_state.user_info)
        st.success("✅ 基本情報を保存しました！")