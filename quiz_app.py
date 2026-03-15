#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
題庫練習應用程式
================

這個簡易的命令列應用程式會讀取由15冊教材萃取出的題庫，
讓使用者選擇冊數與題數後進行練習。題目格式為四選一，
題庫資料存放在同目錄的 ``question_bank.json`` 檔案中。

使用方式：
    python quiz_app.py

程式會提示您選擇冊數與題數，然後依序出題。輸入對應的選項編號
（1–4）即可作答，程式會即時告知正確與否並在最後統計分數。
"""
import json
import os
import random
import sys


def load_question_bank(path: str = 'question_bank.json'):
    """讀取題庫 JSON 資料。"""
    if not os.path.exists(path):
        print(f"找不到題庫檔案 {path}，請確認檔案存在。")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def select_volume(volumes):
    """讓使用者選擇冊數。回傳選擇的冊名或 None 代表全部。"""
    print("\n可選擇的冊數：")
    for idx, vol in enumerate(volumes, start=1):
        print(f"  {idx}. {vol}")
    print("  0. 全部題庫")
    while True:
        choice = input("請輸入欲選擇的冊數編號（0 代表全部）：").strip()
        if choice == '0' or choice == '':
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(volumes):
            return volumes[int(choice) - 1]
        print("輸入無效，請重新輸入。")


def select_question_count(max_count):
    """讓使用者選擇要練習的題數。"""
    default_count = 10
    prompt = f"請輸入要練習的題數（預設 {default_count}，0 或留空代表全部）："
    while True:
        choice = input(prompt).strip()
        if choice == '' or choice == '0':
            return max_count
        if choice.isdigit() and 1 <= int(choice) <= max_count:
            return int(choice)
        print("輸入無效，請重新輸入。")


def run_quiz(questions):
    """執行測驗流程。"""
    random.shuffle(questions)
    num_questions = select_question_count(len(questions))
    score = 0
    for idx, q in enumerate(questions[:num_questions], start=1):
        print(f"\n第 {idx} 題/{num_questions}")
        print(q['question'])

        # 根據實際選項數動態列印，避免選項不足時引發索引錯誤。
        option_count = len(q.get('options', []))
        # 如果沒有選項，提醒使用者並跳過此題
        if option_count == 0:
            print("此題目沒有提供選項，將跳過。")
            continue
        for opt_idx, opt in enumerate(q['options'], start=1):
            print(f"  {opt_idx}. {opt}")

        # 等待使用者答案，根據選項數量調整提示
        while True:
            ans = input(f"你的答案（輸入 1-{option_count}）：").strip()
            # 確認輸入為數字且在合理範圍內
            if ans.isdigit() and 1 <= int(ans) <= option_count:
                break
            print(f"請輸入 1 到 {option_count} 之間的數字。")

        # 正確答案的索引（資料中的 answer_index 從 0 起算）
        correct = q.get('answer_index', -1) + 1
        # 若標註的答案超出選項範圍，當作答案為第一個
        if correct < 1 or correct > option_count:
            correct = 1

        if int(ans) == correct:
            print("答對了！")
            score += 1
        else:
            # 避免索引超出
            correct_option = q['options'][correct - 1] if (0 <= correct - 1 < option_count) else '（答案不存在）'
            print(f"答錯了！正確答案是 {correct}: {correct_option}")
    # 顯示結果
    print("\n測驗結束！")
    print(f"總共答對 {score} 題，共 {num_questions} 題，正確率 {score / num_questions * 100:.1f}%\n")


def main():
    # 讀取題庫
    question_bank = load_question_bank()
    # 取得所有冊數
    volumes = sorted({q['volume'] for q in question_bank})
    # 讓使用者選擇冊數
    selected_volume = select_volume(volumes)
    if selected_volume:
        questions = [q for q in question_bank if q['volume'] == selected_volume]
        print(f"您選擇的冊數：{selected_volume}，共有 {len(questions)} 題。")
    else:
        questions = question_bank
        print(f"您選擇全部題庫，共 {len(questions)} 題。")
    if not questions:
        print("此冊數沒有題目。")
        return
    # 執行測驗
    run_quiz(questions)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n中斷測驗，謝謝使用！")