import fitz
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

# PDFを読み込む
def extract_text_with_hierarchy(pdf_path):
    doc = fitz.open(pdf_path)
    text_data = []

    # フォントサイズとテキストを収集
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_data.append({
                            "text": span["text"].strip(),
                            "font_size": round(span["size"], 2),
                            "page": page_num + 1
                        })

    # フォントサイズの頻度から本文フォントサイズを特定
    font_sizes = [item['font_size'] for item in text_data if item['text']]
    common_font_size = Counter(font_sizes).most_common(1)[0][0]



    # フォントサイズのヒストグラム（累積も）を出力
    plt.figure(figsize=(10, 6))
    plt.hist(font_sizes, bins=len(set(font_sizes)), edgecolor='black', cumulative=True)
    plt.xlabel('Font Size')
    plt.ylabel('Cumulative Frequency')
    plt.title('Cumulative Font Size Histogram')
    plt.savefig('output/cumulative_font_size_histogram.png')
    plt.close()

    # 本文フォントサイズを基準に階層レベルを決定
    unique_font_sizes = sorted(set(font_sizes), reverse=True)
    font_hierarchy = {size: (unique_font_sizes.index(size) + 1) for size in unique_font_sizes}

    # 本文は特別に階層レベルを最大値に設定（最頻フォントサイズ）
    body_level = font_hierarchy[common_font_size]

    # 階層レベル情報を追加
    for item in text_data:
        item['hierarchy_level'] = font_hierarchy[item['font_size']]
        item['is_body'] = item['font_size'] == common_font_size

    return pd.DataFrame(text_data)

# 使用例
pdf_path = "sample_pdf/trm_proper.pdf"
df = extract_text_with_hierarchy(pdf_path)

# 結果をCSVに出力
df.to_csv("output/trm_proper_extracted_hierarchy.csv", index=False, encoding='utf-8-sig')

