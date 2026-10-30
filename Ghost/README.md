# 🎃 ゴースト・パティスリー 〜真夜中の怪異調合録〜 (Midnight Ghost Patisserie)

真夜中0時に開店する冥界の洋菓子店を舞台に、訪れる怪異たちの注文と魔導書のヒントから最適なお菓子を調合するシングルページ型 Streamlit ゲームアプリケーションです。

## 動作要件

- Python 3.10 以上
- Streamlit 1.35.0 以上

## ディレクトリ構成

```text
ghost-patisserie/
├── .gitignore
├── requirements.txt
├── README.md
├── app.py                  # エントリポイント・UI描画・状態管理
├── assets/                 # タイトルバナー・客キャラクター・ランク別シェフ立ち絵
│   ├── title_banner.jpg
│   ├── stage1_jack.jpg
│   ├── stage2_vampire.jpg
│   ├── stage3_wraith.jpg
│   ├── chef_rank_s.jpg
│   ├── chef_rank_a.jpg
│   ├── chef_rank_b.jpg
│   └── chef_rank_c.jpg
├── data/
│   └── stages.py           # ステージデータ・モンスターセリフ・正解定義
└── logic/
    ├── __init__.py
    └── evaluator.py        # 調合スコア判定・フィードバック生成
```

## ローカル実行手順

```bash
# 仮想環境の作成と有効化
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# アプリケーションの起動
.venv/bin/streamlit run app.py
```

## Streamlit Community Cloud へのデプロイ

1. このディレクトリを GitHub リポジトリへプッシュします。
2. [Streamlit Community Cloud](https://share.streamlit.io/) にログインし、対象リポジトリとブランチを選択します。
3. Main file path に `app.py` を指定して **Deploy** をクリックします。

## ゲームルール・採点仕様

全3ステージ（各100点満点・合計300点満点）で怪異にスイーツを提供します。

- **成分配分（最大60点 / 各20点）**: 甘味・苦味・刺激が目標範囲内なら20点、範囲外でも許容誤差 `±10` 以内なら10点、それ以上離れると0点。
- **調理法（20点）**: 最適な調理法と一致で20点、不一致で0点。
- **刻印呪文（20点）**: 大文字・小文字・前後空白を無視して完全一致で20点、部分一致で10点、不一致で0点。
- **ステージ評価**: `85点以上: Perfect` / `60〜84点: Good` / `59点以下: Bad`
- **総合ランク**:
  - `260〜300点`: ランクS「三ツ星ゴーストパティシエ」
  - `180〜259点`: ランクA「一人前の怪異菓子職人」
  - `100〜179点`: ランクB「見習い悪魔の厨房係」
  - `99点以下`: ランクC「厨房爆破の常習犯」

