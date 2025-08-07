import streamlit as st
import pandas as pd
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from janome.tokenizer import Tokenizer

# ファイルの設定
CSV_FILE = "comments.csv"
FONT_PATH = "fonts/ipag.ttf"

# 初期化
if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
    pd.DataFrame(columns=["comment"]).to_csv(CSV_FILE, index=False)

st.title("💬 自由記述アンケート（日本語ワードクラウド）")

# 入力フォーム
with st.form("comment_form"):
    comment = st.text_area("あなたの意見・感想を自由に記入してください")
    submitted = st.form_submit_button("送信する")

    if submitted and comment.strip():
        pd.DataFrame({"comment": [comment.strip()]}).to_csv(CSV_FILE, mode="a", header=False, index=False)
        st.success("✅ 回答ありがとうございました！")

# データ読み込みとワードクラウド生成
df = pd.read_csv(CSV_FILE)
if len(df) > 0:
    st.subheader("🧠 ワードクラウド（頻出語が大きく表示されます）")

    text = "。".join(df["comment"].dropna().astype(str))

    # ストップワードの定義
    stopwords = set([
        "こと", "もの", "これ", "それ", "あれ", "ため", "よう", "さん", 
        "する", "いる", "ある", "私", "僕", "です", "ます", "ので",
        "ん", "それぞれ", "ところ", "一つ", "ような", "何", "何か", "みたい"
    ])

    # Janomeで形態素解析（名詞抽出＋ストップワード除去）
    t = Tokenizer()
    words = [
        token.surface
        for token in t.tokenize(text)
        if token.part_of_speech.startswith("名詞") and len(token.surface) > 1 and token.surface not in stopwords
    ]

    # ワードクラウド描画
    word_freq = pd.Series(words).value_counts().to_dict()
    if word_freq:
        wc = WordCloud(
            font_path=FONT_PATH,
            background_color="white",
            width=800,
            height=400
        ).generate_from_frequencies(word_freq)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("十分な語が集まっていません。")
else:
    st.info("まだ回答がありません。")

# 管理者モード
with st.expander("🛠 管理者メニュー（教員用）"):
    password = st.text_input("パスワードを入力してください", type="password")
    if password == "santi111":
        if st.button("🧹 データを初期化する"):
            pd.DataFrame(columns=["comment"]).to_csv(CSV_FILE, index=False)
            st.success("データを初期化しました。")
    elif password != "":
        st.error("パスワードが違います。")
