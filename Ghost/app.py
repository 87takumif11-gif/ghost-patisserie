"""ゴースト・パティスリー 〜真夜中の怪異調合録〜（Midnight Ghost Patisserie）

エントリポイント・UI描画・状態管理モジュール。
"""

from __future__ import annotations

import inspect
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from data.stages import COOKING_METHODS, STAGES, StageData, select_random_stages
from logic.evaluator import evaluate_concoction, evaluate_final_rank

PROJECT_ROOT = Path(__file__).resolve().parent
TITLE_BANNER_REL_PATH = "assets/title_banner.jpg"
STAGE_IMAGE_FALLBACKS: dict[int, str] = {
    1: "assets/stage1_jack.jpg",
    2: "assets/stage2_vampire.jpg",
    3: "assets/stage3_wraith.jpg",
}
RANK_CHEF_IMAGE_FALLBACKS: dict[str, str] = {
    "S": "assets/chef_rank_s.jpg",
    "A": "assets/chef_rank_a.jpg",
    "B": "assets/chef_rank_b.jpg",
    "C": "assets/chef_rank_c.jpg",
}
_IMAGE_PARAMS = inspect.signature(st.image).parameters
_ST_IMAGE_SUPPORTS_STRETCH = "width" in _IMAGE_PARAMS and isinstance(
    _IMAGE_PARAMS["width"].default, str
)
_ST_IMAGE_SUPPORTS_CONTAINER_WIDTH = "use_container_width" in _IMAGE_PARAMS
_ST_CONTAINER_SUPPORTS_KEY = "key" in inspect.signature(st.container).parameters

st.set_page_config(
    page_title="ゴースト・パティスリー 〜真夜中の怪異調合録〜",
    page_icon="🎃",
    layout="centered",
    initial_sidebar_state="expanded",
)


def _inject_custom_styles() -> None:
    """ハロウィン・ゴシック調の装飾スタイルとブラウザ自動翻訳防止設定を適用する。"""
    st.markdown(
        """
        <meta name="google" content="notranslate">
        <style>
        .patisserie-banner {
            background: linear-gradient(135deg, #1a0b2e 0%, #3b1254 55%, #5c1d3d 100%);
            border: 2px solid #f59e0b;
            border-radius: 16px;
            padding: 2rem 1.5rem;
            text-align: center;
            color: #fef3c7;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
            margin-bottom: 1.5rem;
        }
        .patisserie-banner h1 {
            color: #fbbf24 !important;
            font-size: 2rem;
            margin-bottom: 0.4rem;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
        }
        .patisserie-banner .subtitle {
            color: #e9d5ff;
            font-size: 1rem;
            letter-spacing: 0.08em;
            margin-bottom: 0.8rem;
        }
        .patisserie-banner .ornament {
            font-size: 1.8rem;
            letter-spacing: 0.4rem;
        }
        .rank-card {
            background: linear-gradient(135deg, #24123b 0%, #3d1a52 100%);
            border: 2px solid #fbbf24;
            border-radius: 14px;
            padding: 1.5rem;
            text-align: center;
            color: #fef3c7;
            margin: 1rem 0 1.5rem 0;
        }
        .rank-card .rank-badge {
            font-size: 3rem;
            font-weight: 800;
            color: #fbbf24;
            line-height: 1.1;
        }
        .rank-card .rank-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #fde68a;
            margin-top: 0.4rem;
        }
        .rank-card .rank-desc {
            color: #e9d5ff;
            margin-top: 0.6rem;
            font-size: 0.95rem;
        }
        [data-testid="stImage"] img {
            border-radius: 14px;
            border: 2px solid rgba(245, 158, 11, 0.65);
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
        }
        iframe[height="0"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
        <script>
        try {
            const root = window.parent.document.documentElement;
            root.setAttribute("lang", "ja");
            root.setAttribute("translate", "no");
            root.classList.add("notranslate");
        } catch (e) {}
        </script>
        """,
        height=0,
    )


def _safe_chat_avatar(avatar: str) -> str:
    """st.chat_message 用に複合絵文字（ZWJ等）から先頭の単一絵文字コードポイントを抽出する。"""
    return avatar[0] if avatar else "👻"


@st.cache_data(show_spinner=False)
def _load_image_bytes(abs_path_str: str) -> bytes:
    """画像ファイルをバイト列として読み込みキャッシュする（日本語パス環境でも確実に描画するため）。"""
    return Path(abs_path_str).read_bytes()


def _resolve_stage_image(stage_id: int, image_rel_path: str = "") -> str:
    """ステージIDと相対パスから有効な画像相対パスを解決する。"""
    return image_rel_path or STAGE_IMAGE_FALLBACKS.get(stage_id, "")


def _render_image(rel_path: str, caption: str | None = None) -> bool:
    """アセット画像を横幅いっぱいに描画する（Streamlit バージョン・日本語パス互換対応）。"""
    if not rel_path:
        return False
    img_path = PROJECT_ROOT / rel_path
    if not img_path.is_file():
        return False
    img_bytes = _load_image_bytes(str(img_path))
    if _ST_IMAGE_SUPPORTS_STRETCH:
        st.image(img_bytes, caption=caption, width="stretch")
    elif _ST_IMAGE_SUPPORTS_CONTAINER_WIDTH:
        st.image(img_bytes, caption=caption, use_container_width=True)
    else:
        st.image(img_bytes, caption=caption, use_column_width=True)
    return True


def init_session_state() -> None:
    """st.session_state の初期値を設定する。"""
    defaults: dict[str, object] = {
        "game_state": "TITLE",
        "current_stage_idx": 0,
        "total_score": 0,
        "stage_logs": [],
        "last_evaluation": {},
        "play_round": 0,
    }
    for key, default_val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_val
    if "active_stages" not in st.session_state:
        st.session_state.active_stages = select_random_stages()


def _get_active_stages() -> list[StageData]:
    """現在進行中の3ステージ配列を取得する。"""
    stages = st.session_state.get("active_stages")
    if isinstance(stages, list) and len(stages) > 0:
        return stages
    fresh = select_random_stages()
    st.session_state.active_stages = fresh
    return fresh


def reset_game_data(next_state: str = "TITLE") -> None:
    """ゲーム進行データを初期化し、各キャラクターの注文パターンを再抽選する。"""
    st.session_state.game_state = next_state
    st.session_state.current_stage_idx = 0
    st.session_state.total_score = 0
    st.session_state.stage_logs = []
    st.session_state.last_evaluation = {}
    st.session_state.play_round = int(st.session_state.get("play_round", 0)) + 1
    st.session_state.active_stages = select_random_stages()


def _on_start_game() -> None:
    """タイトル画面からゲームを開始するコールバック。"""
    reset_game_data(next_state="PLAYING")


def _on_submit_concoction(stage: StageData, widget_suffix: str) -> None:
    """調合結果を採点して結果画面へ遷移するコールバック。"""
    sweetness = int(st.session_state.get(f"sweet_{widget_suffix}", 50))
    bitterness = int(st.session_state.get(f"bitter_{widget_suffix}", 50))
    spiciness = int(st.session_state.get(f"spicy_{widget_suffix}", 50))
    selected_method = str(
        st.session_state.get(f"method_{widget_suffix}", COOKING_METHODS[0])
    )
    spell_text = str(st.session_state.get(f"spell_{widget_suffix}", ""))

    evaluation = evaluate_concoction(
        stage=stage,
        sweetness=sweetness,
        bitterness=bitterness,
        spiciness=spiciness,
        method=selected_method,
        spell=spell_text,
    )
    st.session_state.last_evaluation = evaluation
    st.session_state.total_score += evaluation["score"]
    st.session_state.stage_logs.append(evaluation)
    st.session_state.game_state = "RESULT"


def _on_next_stage() -> None:
    """次のステージの客へ進むコールバック。"""
    st.session_state.current_stage_idx += 1
    st.session_state.game_state = "PLAYING"


def _on_finish_day() -> None:
    """全ステージ終了後にエンディング画面へ遷移するコールバック。"""
    st.session_state.game_state = "ENDING"


def _on_restart_game() -> None:
    """エンディング画面からタイトル画面へ戻るコールバック。"""
    reset_game_data(next_state="TITLE")


def render_sidebar(current_stage: StageData | None = None) -> None:
    """プレイ中のサイドバー（進行状況・魔導書）を描画する。"""
    with st.sidebar:
        st.header("📖 真夜中の魔導書")

        active_stages = _get_active_stages()
        total_stages = len(active_stages)
        idx = st.session_state.current_stage_idx
        completed_or_current = min(idx + 1, total_stages)

        st.subheader("🕯️ 今夜の進行状況")
        st.progress(
            completed_or_current / total_stages,
            text=f"来客 {completed_or_current} / {total_stages} 人目",
        )
        st.caption(f"現在の累積スコア: **{st.session_state.total_score} / {total_stages * 100} 点**")

        st.divider()

        if current_stage is not None:
            st.subheader("🔮 客人の観察メモ（ヒント）")
            st.info(current_stage["hint"])

        with st.expander("🧪 魔界素材の特性", expanded=True):
            st.markdown(
                """
                - **🎃 カボチャエキス（甘味）**  
                  霊魂を優しく包み込み、活力を灯す濃密な甘み。
                - **☕ 魔女の泥コーヒー（苦味）**  
                  幾星霜の闇を煮詰めた、高貴で重厚なビターエキス。
                - **🌶️ ドラゴンの毒息（刺激）**  
                  眠れる記憶や感覚をビリビリと呼び覚ます強烈なスパイス。
                """
            )

        with st.expander("🔥 秘伝の調理法", expanded=False):
            st.markdown(
                """
                - **暗闇霊気熟成**: 火も氷も使わず、真夜中の霊気にさらしてじっくり馴染ませる。
                - **怨念直火焼き**: 業火で一気に焼き上げ、芯まで熱々の香ばしさを宿す。
                - **絶対零度冷却**: 冥府の吹雪で瞬時に凍らせ、鋭い冷気を閉じ込める。
                """
            )

        with st.expander("✒️ 仕上げの刻印（呪文）", expanded=False):
            st.markdown(
                """
                お菓子に魂を宿す**英単語の合言葉**。  
                大文字・小文字は問わないが、正確な綴りで刻むほど強い魔力を放つ。
                """
            )


def render_title_screen() -> None:
    """タイトル画面 (game_state == 'TITLE') を描画する。"""
    st.markdown(
        """
        <div class="patisserie-banner">
            <div class="ornament">🎃 🕯️ 🦇 👻 🍰</div>
            <h1>ゴースト・パティスリー</h1>
            <div class="subtitle">〜 真夜中の怪異調合録 / Midnight Ghost Patisserie 〜</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_image(TITLE_BANNER_REL_PATH)

    st.markdown(
        """
        ### 🌙 真夜中0時、怪異たちだけの洋菓子店が幕を開ける——

        ここは人間界と冥界の狭間に佇む小さな洋菓子店**「ゴースト・パティスリー」**。  
        ハロウィンの夜、あなたの店には一癖も二癖もある**3人の怪異のお客様**が訪れます。

        彼らの曖昧でワガママな注文から真の好みを見抜き、  
        **「甘味・苦味・刺激」の3素材**、**「秘伝の調理法」**、そして仕上げの**「刻印呪文」**を調合して、  
        魂を震わせる至高の一皿を差し出しましょう！
        """
    )

    with st.container(border=True):
        st.markdown(
            """
            **📜 店主の心得（遊び方）**
            1. 客人のセリフとサイドバーの**『真夜中の魔導書』**から好みのヒントを読み解く
            2. **3つの素材スライダー**・**調理法**・**刻印呪文**を決定して調合する
            3. 全3ステージ（各100点満点・合計300点満点）で**ランクS「三ツ星ゴーストパティシエ」**を目指そう！
            """
        )

    st.write("")
    st.button(
        "夜の厨房に入る (ゲーム開始)",
        key="btn_start_game",
        type="primary",
        use_container_width=True,
        on_click=_on_start_game,
    )


def render_playing_screen() -> None:
    """プレイ画面 (game_state == 'PLAYING') を描画する。"""
    active_stages = _get_active_stages()
    stage_idx: int = st.session_state.current_stage_idx
    stage: StageData = active_stages[stage_idx]
    sid = stage["id"]

    render_sidebar(current_stage=stage)

    pattern_title = stage.get("pattern_title", "")
    subtitle_suffix = f"（注文：『{pattern_title}』）" if pattern_title else ""
    st.subheader(f"🕯️ 第 {sid} 夜のお客様{subtitle_suffix}")

    # 上部: キャラクターイラスト ＋ モンスターのアバター・名前・オーダーテキスト
    stage_img = _resolve_stage_image(sid, stage.get("image", ""))
    portrait_col, order_col = st.columns([1, 2])
    with portrait_col:
        _render_image(stage_img)
    with order_col:
        with st.chat_message(
            name=stage["name"],
            avatar=_safe_chat_avatar(stage["avatar"]),
        ):
            st.markdown(f"**{stage['avatar']} {stage['name']}**")
            st.markdown(stage["story"])

    st.divider()

    # 中央: 調理エリア
    play_round = int(st.session_state.get("play_round", 0))
    widget_suffix = f"{play_round}_{sid}"

    st.markdown("### 🥣 魔導調合テーブル")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.slider(
            "🎃 カボチャエキス（甘味）",
            min_value=0,
            max_value=100,
            value=50,
            key=f"sweet_{widget_suffix}",
        )
    with col2:
        st.slider(
            "☕ 魔女の泥コーヒー（苦味）",
            min_value=0,
            max_value=100,
            value=50,
            key=f"bitter_{widget_suffix}",
        )
    with col3:
        st.slider(
            "🌶️ ドラゴンの毒息（刺激）",
            min_value=0,
            max_value=100,
            value=50,
            key=f"spicy_{widget_suffix}",
        )

    st.selectbox(
        "🔥 調理法選択",
        options=COOKING_METHODS,
        index=0,
        key=f"method_{widget_suffix}",
    )

    st.text_input(
        "✒️ 仕上げの刻印（呪文入力）",
        placeholder="観察メモをヒントに思いついた英単語を刻む",
        key=f"spell_{widget_suffix}",
    )

    st.write("")

    # 下部: 提出ボタン（on_click で描画前に状態遷移することで前画面要素の残存を防止）
    st.button(
        "✨ お菓子を差し出す",
        key=f"btn_submit_{widget_suffix}",
        type="primary",
        use_container_width=True,
        on_click=_on_submit_concoction,
        args=(stage, widget_suffix),
    )


def render_result_screen() -> None:
    """ステージ結果画面 (game_state == 'RESULT') を描画する。"""
    evaluation = st.session_state.last_evaluation
    render_sidebar(current_stage=None)

    if not evaluation:
        st.session_state.game_state = "TITLE"
        st.rerun()
        return

    rank_key: str = evaluation["rank_key"]
    rank_label: str = evaluation["rank_label"]
    score: int = evaluation["score"]

    st.subheader(f"🍽️ 第 {evaluation['stage_id']} 夜・試食審査結果")

    # ランク別演出
    if rank_key == "perfect":
        st.balloons()
        st.success("🌟 **Perfect!!** 怪異の魂が歓喜に震えています！")
    elif rank_key == "good":
        st.info("✨ **Good!** まずまずの出来栄えで満足してもらえました。")
    else:
        st.error("💥 **Bad...** 客人の機嫌を損ねてしまいました…！")

    # スコア表示
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric(
            label="今回の調合スコア",
            value=f"{score} / 100 点",
            delta=f"判定: {rank_label}",
        )
    with metric_col2:
        st.metric(
            label="現在の累積スコア",
            value=f"{st.session_state.total_score} 点",
        )

    # モンスターのイラストとリアクション
    eval_img = _resolve_stage_image(evaluation["stage_id"], evaluation.get("image", ""))
    portrait_col, react_col = st.columns([1, 2])
    with portrait_col:
        _render_image(eval_img)
    with react_col:
        with st.chat_message(
            name=evaluation["stage_name"],
            avatar=_safe_chat_avatar(evaluation["avatar"]),
        ):
            st.markdown(f"**{evaluation['avatar']} {evaluation['stage_name']}**")
            st.markdown(evaluation["reaction"])

    # 採点内訳・フィードバック
    with st.container(border=True):
        st.markdown("#### 📋 調合フィードバック内訳")
        breakdown = evaluation["breakdown"]
        b_col1, b_col2, b_col3 = st.columns(3)
        b_col1.metric("成分配分", f"{breakdown['ingredients_total']} / 60")
        b_col2.metric("調理法", f"{breakdown['method']} / 20")
        b_col3.metric("刻印呪文", f"{breakdown['spell']} / 20")

        for msg in evaluation["feedback_messages"]:
            st.write(msg)

    st.write("")

    active_stages = _get_active_stages()
    is_last_stage = st.session_state.current_stage_idx >= len(active_stages) - 1
    result_btn_suffix = f"{st.session_state.get('play_round', 0)}_{evaluation['stage_id']}"
    if not is_last_stage:
        st.button(
            "次の客を迎える",
            key=f"btn_next_{result_btn_suffix}",
            type="primary",
            use_container_width=True,
            on_click=_on_next_stage,
        )
    else:
        st.button(
            "本日の営業を終了する",
            key=f"btn_finish_{result_btn_suffix}",
            type="primary",
            use_container_width=True,
            on_click=_on_finish_day,
        )


def render_ending_screen() -> None:
    """エンディング画面 (game_state == 'ENDING') を描画する。"""
    total_score: int = st.session_state.total_score
    final_result = evaluate_final_rank(total_score)

    if final_result["effect"] == "balloons":
        st.balloons()
    elif final_result["effect"] == "snow":
        st.snow()

    st.markdown(
        """
        <div class="patisserie-banner">
            <div class="ornament">🕯️ 🏆 🎃 🏆 🕯️</div>
            <h1>本日の営業終了</h1>
            <div class="subtitle">〜 真夜中の怪異調合録・総合査定 〜</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chef_img = final_result.get("image") or RANK_CHEF_IMAGE_FALLBACKS.get(
        final_result["rank"], ""
    )

    chef_col, rank_col = st.columns([1, 1.35])
    with chef_col:
        _render_image(chef_img)
    with rank_col:
        st.markdown(
            f"""
            <div class="rank-card" style="margin-top: 0;">
                <div>総合ランク</div>
                <div class="rank-badge">RANK {final_result['rank']}</div>
                <div class="rank-title">称号：「{final_result['title']}」</div>
                <div class="rank-desc">{final_result['description']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.metric(label="最終獲得スコア（300点満点）", value=f"{total_score} / 300 点")

    st.divider()
    st.subheader("📜 今夜の調合録（ステージ履歴）")

    for log in st.session_state.stage_logs:
        pattern_title = log.get("pattern_title", "")
        pattern_label = f"『{pattern_title}』" if pattern_title else ""
        with st.expander(
            f"第{log['stage_id']}夜: {log['avatar']} {log['stage_name']}{pattern_label} — "
            f"{log['score']}点 ({log['rank_label']})",
            expanded=False,
        ):
            hist_img_col, hist_txt_col = st.columns([1, 3])
            with hist_img_col:
                _render_image(_resolve_stage_image(log["stage_id"], log.get("image", "")))
            with hist_txt_col:
                st.markdown(f"**客人の反応:** {log['reaction']}")
                inputs = log["inputs"]
                st.caption(
                    f"調合レシピ: 甘味 {inputs['sweetness']} / 苦味 {inputs['bitterness']} / "
                    f"刺激 {inputs['spiciness']} ｜ 調理法: {inputs['method']} ｜ "
                    f"刻印: {inputs['spell'] or '（未入力）'}"
                )
                for msg in log["feedback_messages"]:
                    st.write(msg)

    st.write("")
    st.button(
        "もう一度店を開く",
        key=f"btn_restart_{st.session_state.get('play_round', 0)}",
        type="primary",
        use_container_width=True,
        on_click=_on_restart_game,
    )


def main() -> None:
    """アプリケーションのメインルーティング処理。"""
    _inject_custom_styles()
    init_session_state()

    state: str = st.session_state.game_state
    if state not in ("TITLE", "PLAYING", "RESULT", "ENDING"):
        reset_game_data(next_state="TITLE")
        state = "TITLE"

    screen_key = f"screen_{state}_{st.session_state.get('play_round', 0)}_{st.session_state.current_stage_idx}"
    if _ST_CONTAINER_SUPPORTS_KEY:
        screen_ctx = st.container(key=screen_key)
    else:
        screen_ctx = st.empty().container()

    with screen_ctx:
        if state == "TITLE":
            render_title_screen()
        elif state == "PLAYING":
            render_playing_screen()
        elif state == "RESULT":
            render_result_screen()
        elif state == "ENDING":
            render_ending_screen()


if __name__ == "__main__":
    main()
