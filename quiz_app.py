#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit 題庫練習應用程式
===========================

這個 Streamlit 應用程式會讀取由 15 冊教材萃取出的題庫，
讓使用者在網頁介面上選擇冊數與題數後進行練習。每題依照
原題庫的選項數量動態產生單選按鈕，並即時統計分數。

使用方式：
    在命令列執行：
        streamlit run app.py

程式會先讓您選擇要練習的冊數和題數，然後按「開始測驗」
進入測驗流程。每題回答後按「提交答案」，並在最後
顯示答題結果。
"""

import json
import os
import random
import streamlit as st


@st.cache_data
def load_question_bank(path: str = 'question_bank.json'):
    """讀取題庫 JSON 資料並快取結果。

    Args:
        path (str): 題庫檔案路徑。

    Returns:
        list[dict]: 題庫資料，每個元素包含 question、options、answer_index 和 volume。
    """
    if not os.path.exists(path):
        st.error(f"找不到題庫檔案 {path}，請確認檔案存在。")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def get_volumes(question_bank):
    """取得所有冊數列表。"""
    return sorted({q['volume'] for q in question_bank})


def init_session_state():
    """初始化 session_state 中用於測驗的欄位。"""
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'answered' not in st.session_state:
        st.session_state.answered = False


def start_quiz(selected_volume: str, question_count: int, question_bank: list[dict]):
    """根據使用者選擇開始測驗，初始化題目順序與狀態。"""
    # 過濾所選冊數的題目
    if selected_volume == '全部':
        questions = question_bank.copy()
    else:
        questions = [q for q in question_bank if q['volume'] == selected_volume]
    if not questions:
        st.error("所選冊數沒有題目，請重新選擇。")
        return
    # 隨機排序並取前 question_count 題
    random.shuffle(questions)
    question_count = min(question_count, len(questions))
    st.session_state.quiz_questions = questions[:question_count]
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.quiz_started = True


def show_quiz():
    """顯示測驗中的題目、選項與提交/下一題按鈕。"""
    questions = st.session_state.quiz_questions
    idx = st.session_state.current_index
    q = questions[idx]
    total = len(questions)
    st.subheader(f"第 {idx + 1} 題 / {total}")
    st.write(q['question'])
    # 選項數
    option_count = len(q.get('options', []))
    if option_count == 0:
        st.warning("此題目沒有提供選項，已自動跳過。")
        # 跳過此題直接進下一題
        st.session_state.current_index += 1
        if st.session_state.current_index >= total:
            show_result()
            return
        else:
            show_quiz()
            return
    # radio 的 key 必須固定，避免刷新後被重置
    radio_key = f"radio_{idx}"
    # 建立選項編號列表，如 [0, 1, 2, ...]
    choices = list(range(option_count))
    # 顯示選項文字
    choice = st.radio(
        "請選擇答案：",
        options=choices,
        format_func=lambda i: f"{i + 1}. {q['options'][i]}",
        key=radio_key,
        index=0,
        disabled=st.session_state.answered,
    )
    # 如果尚未作答，顯示提交按鈕
    if not st.session_state.answered:
        if st.button("提交答案"):
            correct = q.get('answer_index', 0)
            # 檢查正確答案是否在範圍內
            if correct >= option_count:
                correct = 0
            if choice == correct:
                st.session_state.score += 1
                st.success("答對了！")
            else:
                st.error(f"答錯了！正確答案是 {correct + 1}: {q['options'][correct]}")
            st.session_state.answered = True
    else:
        # 已作答時，顯示下一題按鈕
        if st.button("下一題"):
            st.session_state.current_index += 1
            st.session_state.answered = False
            if st.session_state.current_index >= len(questions):
                show_result()
            else:
                show_quiz()


def show_result():
    """顯示測驗結束的結果與再試一次的按鈕。"""
    total = len(st.session_state.quiz_questions)
    score = st.session_state.score
    st.success("測驗結束！")
    st.write(f"總共答對 {score} 題，共 {total} 題，正確率 {score / total * 100:.1f}%")
    if st.button("再試一次"):
        st.session_state.quiz_started = False
        # 重置其他狀態
        st.session_state.quiz_questions = []
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answered = False


def main():
    st.title("題庫練習應用程式 (Streamlit 版)")
    # 初始化狀態
    init_session_state()
    # 載入題庫
    question_bank = load_question_bank()
    if not question_bank:
        return
    # 側邊欄選擇冊數與題數
    with st.sidebar:
        st.header("設定")
        volumes = get_volumes(question_bank)
        volume_options = ['全部'] + volumes
        selected_volume = st.selectbox("選擇冊數：", options=volume_options)
        # 設定題數輸入範圍
        # 如果選擇全部，最大題數為 20 或全部，避免一次出太多
        max_questions = len(question_bank) if selected_volume == '全部' else sum(1 for q in question_bank if q['volume'] == selected_volume)
        default_questions = min(10, max_questions)
        question_count = st.number_input("練習題數：", min_value=1, max_value=max_questions, value=default_questions, step=1)
        if not st.session_state.quiz_started:
            if st.button("開始測驗"):
                start_quiz(selected_volume, int(question_count), question_bank)
    # 測驗流程
    if st.session_state.quiz_started:
        show_quiz()


if __name__ == '__main__':
    main()