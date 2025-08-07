import streamlit as st
import pandas as pd
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import MeCab

# ファイルの設定
CSV_FILE = "comments.csv"
FONT_PATH = "fonts/ipagp.ttf"  # フォントをfontsフォルダに置くこと

# 初期化：ファイルがなければ作成
if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
    pd.DataFrame(columns=["comment"]).to_csv(CSV_FILE, index=False)

# タイトル
st.title("💬 自由記述アンケート（日本語ワードクラウド）")

# 回答フォーム
with st.form("comment_form"):
    comment = st.text_area("あなたの意見・感想を自由に記入してください")
    submitted = st.form_submit_button("送信する")

    if submitted and comment.strip():
        pd.DataFrame({"comment": [comment.strip()]}).to_csv(CSV_FILE, mode="a", header=False, index=False)
        st.success("✅ 回答ありがとうございました！")

# データの読み込み
df = pd.read_csv(CSV_FILE)
if len(df) > 0:
    st.subheader("🧠 ワードクラウド（出現頻度が高い語ほど大きく表示）")

    # 全コメントを連結
    text = "。".join(df["comment"].dropna().astype(str))

    # ストップワードの定義（必要に応じて追加）
    stopwords = set([
        "こと", "もの", "これ", "それ", "あれ", "ため", "よう", "さん", 
        "する", "いる", "ある", "私", "僕", "です", "ます", "ので", 
        "ん", "それぞれ", "ところ", "一つ", "ような", "何", "何か", "みたい"
    ])

    # MeCabで名詞を抽出してストップワードを除外
    tagger = MeCab.Tagger("-Ochasen")
    node = tagger.parseToNode(text)
    words = []

    while node:
        surface = node.surface
        if node.feature.startswith("名詞") and len(surface) > 1:
            if surface not in stopwords:
                words.append(surface)
        node = node.next

    # 頻度集計
    word_freq = pd.Series(words).value_counts().to_dict()

    # ワードクラウド描画
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

# 管理者メニュー（リセット）
with st.expander("🛠 管理者メニュー（教員用）"):
    password = st.text_input("パスワードを入力してください", type="password")
    if password == "santi111":
        if st.button("🧹 データを初期化する"):
            pd.DataFrame(columns=["comment"]).to_csv(CSV_FILE, index=False)
            st.success("データを初期化しました。")
    elif password != "":
        st.error("パスワードが違います。")

