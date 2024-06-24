import streamlit as st
from utils import load_data, save_data
import os
import pandas as pd


# ファイルパスの設定
FILE_PATH = 'data/mahjong_scores.pkl'
PENDING_PATH = 'data/pending_scores.pkl'
OPPONENTS_PATH = 'data/opponents_data.pkl'
RESERVATION_PATH = 'data/mahjong_reservations.pkl'
INDIVIDUAL_FILE_PATH = 'data/individual_scores.pkl'
PLAYER_POINT_PATH = 'data/player_data.pkl' 


# 管理者のユーザー名とパスワード
ADMIN_PASSWORD = '5959'

def modify_score(scores, team, round_index, new_score, majan_type):
    try:
        scores[team][round_index] = (new_score, majan_type)
        save_data(scores, FILE_PATH)
        return True
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return False

def modify_individual_score(individual_scores, player, round_index, new_score, majan_type):
    try:
        individual_scores[player][round_index] = (new_score, majan_type)
        save_data(individual_scores, INDIVIDUAL_FILE_PATH)
        return True
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return False

def delete_score(scores, team, round_index):
    try:
        scores[team].pop(round_index)
        save_data(scores, FILE_PATH)
        return True
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return False

def delete_individual_score(individual_scores, player, round_index):
    try:
        individual_scores[player].pop(round_index)
        save_data(individual_scores, INDIVIDUAL_FILE_PATH)
        return True
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return False

def admin_interface():
    st.sidebar.title("管理者ページ")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:

        # データのロード
        scores = load_data(FILE_PATH)
        pending_scores = load_data(PENDING_PATH)
        individual_scores = load_data(INDIVIDUAL_FILE_PATH)

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
                    player_name = player_display.split(" - ")[1]
                    if not is_approved:
                        if team_name not in scores:
                            scores[team_name] = []
                        scores[team_name].append((adjusted_score, majan_type))

                        if player_name not in individual_scores:
                            individual_scores[player_name] = []
                        individual_scores[player_name].append((adjusted_score, majan_type))

                del pending_scores[selected_game_id]  # 承認後、この試合IDを削除
                game_ids.remove(selected_game_id)  # リストからも削除
                save_data(pending_scores, PENDING_PATH)
                save_data(scores, FILE_PATH)
                save_data(individual_scores, INDIVIDUAL_FILE_PATH)
                save_data(opponents_data, OPPONENTS_PATH)
                st.experimental_rerun()

            if columns[1].button('却下'):
                del pending_scores[selected_game_id]  # 却下後、この試合IDを削除
                game_ids.remove(selected_game_id)  # リストからも削除
                save_data(pending_scores, PENDING_PATH)
                st.experimental_rerun()

        # チームを選択
        selected_team = st.sidebar.selectbox('修正したいチームを選択してください', [''] + list(scores.keys()), index=0)
        if selected_team:
            # 選択されたチームの回数を選択
            rounds = scores[selected_team]
            round_options = [(i, score, majan_type) for i, (score, majan_type) in enumerate(rounds, start=1)]
            selected_round_index = st.sidebar.selectbox('修正したいデータの回数を選択してください', round_options, format_func=lambda x: f"第{x[0]}回目のスコア: {x[1]} 点, {'三' if x[2] == '3' else '四'}麻")

            if selected_round_index is not None:
                selected_round = rounds[selected_round_index[0] - 1]
                st.sidebar.subheader(f"第{selected_round_index[0]}回目のスコア")

                # 修正後の点数を入力
                new_score = st.sidebar.number_input('修正後の点数を入力してください', min_value=-1000000)

                # 修正ボタンと削除ボタンを横並びに配置
                col1, col2 = st.sidebar.columns(2)

                with col1:
                    if st.button('修正'):
                        # 修正処理の呼び出し
                        if modify_score(scores, selected_team, selected_round_index[0] - 1, new_score, selected_round_index[2]):
                            st.sidebar.success('スコアが修正されました。')
                        else:
                            st.sidebar.error('スコアの修正に失敗しました。')

                with col2:
                    if st.button('削除'):
                        # 削除処理の呼び出し
                        if delete_score(scores, selected_team, selected_round_index[0] - 1):
                            st.sidebar.success('スコアが削除されました。')
                        else:
                            st.sidebar.error('スコアの削除に失敗しました。')

        # プレイヤーを選択
        selected_player = st.sidebar.selectbox('修正したいプレイヤーを選択してください', [''] + list(individual_scores.keys()), index=0)
        if selected_player:
            # 選択されたプレイヤーの回数を選択
            rounds = individual_scores[selected_player]
            round_options = [(i, score, majan_type) for i, (score, majan_type) in enumerate(rounds, start=1)]
            selected_round_index = st.sidebar.selectbox('修正したいデータの回数を選択してください', round_options, format_func=lambda x: f"第{x[0]}回目のスコア: {x[1]} 点, {'三' if x[2] == '3' else '四'}麻")

            if selected_round_index is not None:
                selected_round = rounds[selected_round_index[0] - 1]
                st.sidebar.subheader(f"第{selected_round_index[0]}回目のスコア")

                # 修正後の点数を入力
                new_score = st.sidebar.number_input('修正後の点数を入力してください', min_value=-1000000, max_value=1000000, value=selected_round[0])

                # 修正ボタンと削除ボタンを横並びに配置
                col1, col2 = st.sidebar.columns(2)

                with col1:
                    if st.button('修正'):
                        # 修正処理の呼び出し
                        if modify_individual_score(individual_scores, selected_player, selected_round_index[0] - 1, new_score, selected_round_index[2]):
                            st.sidebar.success('スコアが修正されました。')
                        else:
                            st.sidebar.error('スコアの修正に失敗しました。')

                with col2:
                    if st.button('削除'):
                        # 削除処理の呼び出し
                        if delete_individual_score(individual_scores, selected_player, selected_round_index[0] - 1):
                            st.sidebar.success('スコアが削除されました。')
                        else:
                            st.sidebar.error('スコアの削除に失敗しました。')
        # ランキングの表示
        st.title('ランキング')

        # 登録されたデータを読み込み
        data = load_data(PLAYER_POINT_PATH)

        # スコアでソート
        sorted_data = sorted(data, key=lambda x: x['player_point'], reverse=True)

        # データフレームに変換
        df = pd.DataFrame(sorted_data)
        df.index = df.index + 1  # インデックスを1から始める

        # テーブルとして表示
        st.table(df)

    else:
        st.sidebar.title("ログイン")
        password = st.sidebar.text_input("パスワード", type='password')
        if st.sidebar.button('ログイン'):
            if password == ADMIN_PASSWORD:
                st.session_state['logged_in'] = True
                st.experimental_rerun()
            else:
                st.sidebar.error("ユーザー名またはパスワードが間違っています。")
