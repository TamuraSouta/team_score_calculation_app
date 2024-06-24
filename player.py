import streamlit as st
from utils import load_data, save_data
from datetime import datetime
import random
import matplotlib.pyplot as plt
import numpy as np  # NumPy モジュールをインポート
import japanize_matplotlib
import pandas as pd




# ファイルパスの設定
FILE_PATH = 'data/mahjong_scores.pkl'
PENDING_PATH = 'data/pending_scores.pkl'
PLAYER_POINT_PATH = 'data/player_data.pkl' 


sanma_kaesiten = 15000
sanma_penalty = 40000
yonma_kaesiten = 20000
yonma_penalty = 30000

janreki_regulation = 3
sanma_regulation = 1
yonma_regulation = 1.5


teams = {
    "織姫": ["すじこちゃん", "ak9", "hama", "ふゆりり", "たむら"],
    "彦星": ["リキチ", "優馬", "なみゅーる", "おっちゃん", "満貫"],
}
# 段位とポイントの対応表
dan_points = {
    "初心1": 1,
    "初心2": 2,
    "初心3": 3,
    "雀士1": 4,
    "雀士2": 5,
    "雀士3": 6,
    "雀傑1": 7,
    "雀傑2": 8,
    "雀傑3": 9,
    "雀豪1": 10,
    "雀豪2": 12,
    "雀豪3": 14,
    "雀聖1": 16,
    "雀聖2": 18,
    "雀聖3": 20,
}

def player_interface():
    st.title('麻雀アプリ')
    with st.expander('対戦スコアを入力'):
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
                pending_scores = load_data(PENDING_PATH)
                if game_id not in pending_scores:
                    pending_scores[game_id] = {}
                total_input_score = 0  # 入力されたスコアの合計値を初期化

                player_scores = {}
                original_scores = {}

                for player_display in selected_players:
                    team_name, player_name = player_display.split(" - ")
                    input_score = st.session_state[f'score_{player_name}']
                    player_scores[player_name] = input_score
                    original_scores[player_name] = input_score
                    total_input_score += input_score  # 各プレイヤーのスコアを合計に加算

                if (game_type == "3" and total_input_score == 105000) or (game_type == "4" and total_input_score == 100000):
                    if game_type == "3":
                        penalty = sanma_penalty
                        bonus = sanma_kaesiten
                    else:
                        penalty = yonma_penalty
                        bonus = yonma_kaesiten


                    # 一位のプレイヤーにボーナス点を加算
                    top_player = max(player_scores, key=lambda k: player_scores[k] + penalty)
                    player_scores[top_player] += bonus

                    for player_display in selected_players:
                        team_name, player_name = player_display.split(" - ")
                        input_score = player_scores[player_name]
                        adjusted_score = input_score - penalty
                        pending_scores[game_id][player_display] = [team_name, input_score, adjusted_score, False, game_type]
                        st.success(f"試合ID {player_display} {original_scores[player_name]} の点数申請を受け付けました。")

                    save_data(pending_scores, PENDING_PATH)
                    st.success(f"試合ID {game_id} の点数申請を受け付けました。")

                else:
                    st.warning("入力値が正しいか確認してください")
        else:
            st.warning('3人または4人のプレイヤーを選択してください。')

    # チームの合計点数を表示するボタン
    with st.expander('チームの合計点数'):
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
            ax.text(bar.get_x() + bar.get_width() / 2, yval, round(score, 1), ha='center', va='bottom', color='black', fontsize=12, fontweight='bold')

        st.pyplot(fig)


    # プレイヤー情報登録ボタン
    with st.expander('プレイヤー情報を入力'):
        # プレイヤー名のテキスト入力
        selected_player = st.text_input('オプチャ名を入力してください（8文字以内）', max_chars=8)

        # 雀歴の入力
        st.write("雀歴を入力してください")
        col1, col2 = st.columns([1, 1])
        with col1:
            years = st.number_input('年', min_value=0, max_value=100, step=1)
        with col2:
            months = st.number_input('月', min_value=0, max_value=12, step=1)
        janreki = round((years + months/12) * janreki_regulation, 2)

        # 段位のセレクトボックス
        st.write("雀魂の段位を選択してください")
        col3, col4 = st.columns([1, 1])
        with col3:
            sanma_lank = st.selectbox('三麻段位', list(dan_points.keys()), key='sanma')
        with col4:
            yonma_lank = st.selectbox('四麻段位', list(dan_points.keys()), key='yonma')

        sanma_points = dan_points[sanma_lank]
        yonma_points = dan_points[yonma_lank]

        lank_point = sanma_points * sanma_regulation + yonma_points * yonma_regulation
        
        player_point = round(janreki + lank_point, 2)

        # ルール確認のチェックボックス
        rules_confirmed = st.checkbox('大会ルールの内容に同意する')

        # すべての情報が正しく入力されているか確認
        all_fields_filled = selected_player and sanma_lank and yonma_lank and years is not None and months is not None

        # 登録ボタン
        register_button = st.button('登録', disabled=not (rules_confirmed and all_fields_filled))
        if register_button:
            player_data = {'プレイヤー名': selected_player, 'player_point': player_point}
            data = load_data(PLAYER_POINT_PATH)
            if not isinstance(data, list):
                data = []

            # プレイヤー名が既に存在する場合は更新、存在しない場合は追加
            player_exists = False
            for i, existing_player in enumerate(data):
                if existing_player['プレイヤー名'] == selected_player:
                    data[i] = player_data
                    player_exists = True
                    break
            if not player_exists:
                data.append(player_data)

            save_data(data, PLAYER_POINT_PATH) 
            st.success(f'{selected_player}のデータが登録されました。')
        
        # 登録されたデータを読み込み

        # 登録されたデータを読み込み
        data = load_data(PLAYER_POINT_PATH)

        # プレイヤー名のみのリストを作成
        participant_names = [player['プレイヤー名'] for player in data]

        # 参加者名をカンマ区切りで表示
        st.write('参加者: ' + ', '.join(participant_names))



    # mahjong_scores = load_data(FILE_PATH)
    # st.write(mahjong_scores)
