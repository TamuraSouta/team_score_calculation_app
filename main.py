import streamlit as st
import os
import pandas as pd
import pickle
from datetime import datetime
import random
import matplotlib.pyplot as plt
import numpy as np  # NumPy モジュールをインポート



# データを保存・読み込むためのファイルパス
FILE_PATH = 'mahjong_scores.pkl'
PENDING_PATH = 'pending_scores.pkl'
OPPONENTS_PATH = 'opponents_data.pkl' 
RESERVATION_PATH = 'mahjong_reservations.pkl'

# 管理者のユーザー名とパスワード
ADMIN_PASSWORD = '5959'

teams = {
    "A": ["トト丸", "すじこちゃん", "蒼瀬"],
    "B": ["すだち油", "とまと", "国士無双待ちたかった"],
    "C": ["たまやん", "たむら", "歩"],
    "D": ["いちまる", "カジキ侍", "海てつお"],
    "E": ["むっかー", "ティアラ", "おっちゃん"],
    "F": ["魚の燻製", "国士無双待ち", "hiro"]
}


def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

def save_data(data, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)

# データのロード
if 'scores' not in st.session_state:
    st.session_state['scores'] = load_data(FILE_PATH)
if 'opponents_data' not in st.session_state:
    st.session_state['opponents_data'] = load_data(OPPONENTS_PATH)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'reservations' not in st.session_state:
    st.session_state['reservations'] = load_data(RESERVATION_PATH)


# スコア修正関数
def modify_score(scores, team, round_index, new_score, majan_type):
    try:
        scores[team][round_index] = (new_score, majan_type)
        save_data(scores, FILE_PATH)
        return True
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return False

# スコア削除関数
def delete_score(scores, team, round_index):
    try:
        scores[team].pop(round_index)
        save_data(scores, FILE_PATH)
        return True
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return False


#### 管理者画面　####
if st.session_state['logged_in']:
    st.sidebar.title("管理者ページ")
    
    # データのロード
    scores = load_data(FILE_PATH)
    mahjong_scores = load_data(FILE_PATH)
    pending_scores = load_data(PENDING_PATH)

    # 選択した試合IDのスコア一覧と操作
    game_ids = list(pending_scores.keys())
    selected_game_id = st.sidebar.selectbox("試合IDを選択", game_ids)
    if selected_game_id:
        game_scores = pending_scores[selected_game_id]
        # 各チームのスコアと個別の承認または却下オプション
        for player_display, score_details in list(game_scores.items()):
            team_name, input_score, adjusted_score, is_approved, majan_type = score_details
            if not is_approved:
                st.sidebar.markdown(f"**{player_display}（チーム{team_name}）: {input_score}点**")

        # 全てのスコアを一括で承認と却下
        columns = st.sidebar.columns(2)
        if columns[0].button('承認'):
            opponents_data = load_data(OPPONENTS_PATH)

            # 新たな対戦情報を既存のデータに追加
            for player_display, score_details in game_scores.items():
                team_name, input_score, adjusted_score, is_approved, majan_type = score_details
                if not is_approved:
                    if team_name not in scores:
                        scores[team_name] = []
                    scores[team_name].append((adjusted_score, majan_type))

            del pending_scores[selected_game_id]  # 承認後、この試合IDを削除
            game_ids.remove(selected_game_id)  # リストからも削除
            save_data(pending_scores, PENDING_PATH)
            save_data(scores, FILE_PATH)
            save_data(opponents_data, OPPONENTS_PATH)  
            st.experimental_rerun()

        if columns[1].button(f'却下'):
            del pending_scores[selected_game_id]  # 却下後、この試合IDを削除
            game_ids.remove(selected_game_id)  # リストからも削除
            save_data(pending_scores, PENDING_PATH)
            st.experimental_rerun()

    
    # チームを選択
    selected_team = st.sidebar.selectbox('修正したいチームを選択してください', [''] + list(mahjong_scores.keys()), index=0)
    if selected_team:
        # 選択されたチームの回数を選択
        rounds = mahjong_scores[selected_team]
        round_options = [(i, score, majan_type) for i, (score, majan_type) in enumerate(rounds, start=1)]
        selected_round_index = st.sidebar.selectbox('修正したいデータの回数を選択してください', round_options, format_func=lambda x: f"第{x[0]}回目のスコア: {x[1]} 点, {'三' if x[2] == '3' else '四'}麻")

        if selected_round_index is not None:
            selected_round = rounds[selected_round_index[0] - 1]
            st.sidebar.subheader(f"第{selected_round_index[0]}回目のスコア")
            
            # 修正後の点数を入力
            new_score = st.sidebar.number_input('修正後の点数を入力してください', min_value=-10000)

            # 修正ボタンと削除ボタンを横並びに配置
            col1, col2 = st.sidebar.columns(2)

            with col1:
                if st.button('修正'):
                    # 修正処理の呼び出し
                    if modify_score(mahjong_scores, selected_team, selected_round_index[0] - 1, new_score, selected_round_index[2]):
                        st.sidebar.success('スコアが修正されました。')
                    else:
                        st.sidebar.error('スコアの修正に失敗しました。')

            with col2:
                if st.button('削除'):
                    # 削除処理の呼び出し
                    if delete_score(mahjong_scores, selected_team, selected_round_index[0] - 1):
                        st.sidebar.success('スコアが削除されました。')
                    else:
                        st.sidebar.error('スコアの削除に失敗しました。')


else:
    st.sidebar.title("ログイン")
    password = st.sidebar.text_input("パスワード", type='password')
    if st.sidebar.button('ログイン'):
        if password == ADMIN_PASSWORD:
            st.session_state['logged_in'] = True
            st.experimental_rerun()
        else:
            st.sidebar.error("ユーザー名またはパスワードが間違っています。")

#### プレイヤー画面　####
st.title('麻雀アプリ')


# チーム名とプレイヤー名を組み合わせて選択肢を作成
all_players = [f"{team} - {player}" for team, members in teams.items() for player in members]

# プレイヤーの選択と点数入力
selected_players = st.multiselect('プレイヤーを選択してください（3人または4人）', all_players)
game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M')}_{random.randint(1000, 9999)}"

# スコア入力の初期化と表示
for player_display in selected_players:
    team_name, player_name = player_display.split(" - ")
    if f'score_{player_name}' not in st.session_state:
        st.session_state[f'score_{player_name}'] = 0
    score = st.session_state[f'score_{player_name}']
    st.number_input(f'{player_name}の点数', key=f'score_{player_name}', value=score)

# 点数申請の制御
if len(selected_players) == 3 or len(selected_players) == 4:
    if st.button('点数を申請'):
        game_type = "3" if len(selected_players) == 3 else "4"
        initial_points = 35000 if game_type == "3" else 25000
        pending_scores = load_data(PENDING_PATH)
        if game_id not in pending_scores:
            pending_scores[game_id] = {}
        total_input_score = 0  # 入力されたスコアの合計値を初期化

        for player_display in selected_players:
            team_name, player_name = player_display.split(" - ")
            input_score = st.session_state[f'score_{player_name}']
            total_input_score += input_score  # 各プレイヤーのスコアを合計に加算

        if (game_type == "3" and total_input_score == 105000) or (game_type == "4" and total_input_score == 100000):
            for player_display in selected_players:
                team_name, player_name = player_display.split(" - ")
                input_score = st.session_state[f'score_{player_name}']
                adjusted_score = input_score - initial_points
                pending_scores[game_id][player_display] = [team_name, input_score, adjusted_score, False, game_type]
                st.success(f"試合ID {player_display} {input_score} の点数申請を受け付けました。")

            save_data(pending_scores, PENDING_PATH)
            st.success(f"試合ID {game_id} の点数申請を受け付けました。")

        else:
            st.warning("入力値が正しいか確認してください")
else:
    st.warning('3人または4人のプレイヤーを選択してください。')




# チームの合計点数を表示するボタン
if st.button('チームの合計点数'):
    mahjong_scores = load_data(FILE_PATH)

    # チームごとの合計点数を計算
    team_totals = {}
    for team, games in mahjong_scores.items():
        team_total = sum(game[0] for game in games)
        team_totals[team] = team_total
    
    # チーム名をソート
    sorted_teams = sorted(team_totals.keys())
    sorted_scores = [team_totals[team] for team in sorted_teams]

    # チームの合計点数をグラフで表示
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#f8f9fa')  # 背景色を明るい色に変更
    colors = plt.cm.tab20c(np.linspace(0, 1, len(sorted_teams)))  # 各チームに明るい色を割り当て
    bars = ax.bar(sorted_teams, sorted_scores, color=colors, edgecolor='black', linewidth=1.5)
    
    # タイトルと軸ラベルを設定
    ax.set_title('Teams Scores', fontsize=20, fontweight='bold')
    ax.set_xlabel('Team', fontsize=14, fontweight='bold')
    ax.set_ylabel('Score', fontsize=14, fontweight='bold')
    ax.set_facecolor('#ffffff')  # 軸の背景色も明るい色に変更
    
    # 軸のフォントサイズを調整
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    
    # 各バーにスコアを表示
    for bar, score in zip(bars, sorted_scores):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, round(score, 1), ha='center', va='bottom', color='black', fontsize=12, fontweight='bold')

    st.pyplot(fig)




# # データのロード
# mahjong_scores = load_data(FILE_PATH)

# # データを表示
# st.subheader('保存されている全マージャンスコア:')
# st.write(mahjong_scores)