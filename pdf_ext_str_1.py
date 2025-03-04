import pdfplumber
import fitz  # PyMuPDF
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np


def extract_text_with_hierarchy(pdf_path, output_csv, output_histogram):
    data = []  # CSV保存用のデータ
    font_sizes = Counter()
    extracted_texts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2)  # 文字分断防止
            if text:
                extracted_texts.append((page.page_number, text.split("\n")))
    
    doc = fitz.open(pdf_path)
    text_data = []
    for page in doc:
        for block in page.get_text("blocks"):  # 文字単位での分断を防ぐ
            text = block[4].strip()
            font_size = block[3] if len(block) > 3 else 10  # フォントサイズがある場合のみ取得
            if text:
                text_data.append((page.number + 1, text, font_size))
                font_sizes[font_size] += 1  # フォントサイズの頻度解析
    
    # フォントサイズの累積頻度を計算し、本文とタイトルの閾値を決定
    sorted_sizes = sorted(font_sizes.items())
    total_count = sum(font_sizes.values())
    cumulative_count = 0
    threshold_font_size = None
    
    for size, count in sorted_sizes:
        cumulative_count += count
        if cumulative_count / total_count >= 0.8:
            threshold_font_size = size
            break
    
    # フォントサイズをグループ化（±1pt の誤差を許容）
    unique_sizes = np.array(sorted(font_sizes.keys(), reverse=True))
    grouped_sizes = {}
    level = 1
    
    for size in unique_sizes:
        if size <= threshold_font_size:
            grouped_sizes[size] = 0  # 本文
        else:
            grouped_sizes[size] = level
            level += 1
    
    # ヒストグラムを作成（bin=1）
    plt.figure(figsize=(10, 5))
    plt.hist(list(font_sizes.elements()), bins=range(int(min(font_sizes.keys())), int(max(font_sizes.keys())) + 2, 1), color='b', alpha=0.7, edgecolor='black')
    plt.xlabel("Font Size")
    plt.ylabel("Frequency")
    plt.title("Font Size Frequency Histogram")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(output_histogram)
    plt.close()
    print(f"Saved font size histogram to {output_histogram}")
    
    # テキストと階層情報をリスト化
    for page_num, text, font_size in text_data:
        adjusted_size = min(unique_sizes, key=lambda x: abs(x - font_size))  # ±1pt の誤差を許容
        level = grouped_sizes.get(adjusted_size, 0)  # 本文はレベル0
        data.append([page_num, text, level])
    
    # CSVに保存
    df = pd.DataFrame(data, columns=["Page", "Text", "Hierarchy_Level"])
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")  # 日本語文字化け防止
    print(f"Saved extracted text to {output_csv}")
# 使用例
pdf_path = "./sample_pdf/yva_proper.pdf"
output_csv = "extracted_text.csv"
output_histogram = "text_length_histogram.png"
extract_text_with_hierarchy(pdf_path, output_csv, output_histogram)
