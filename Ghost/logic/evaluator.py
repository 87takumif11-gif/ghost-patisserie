"""調合スコア判定・フィードバック生成モジュール。"""

from __future__ import annotations

from typing import Any

from data.stages import StageData

TOLERANCE: int = 10


def _score_ingredient(
    label: str,
    value: int,
    target_range: tuple[int, int],
) -> tuple[int, str]:
    """成分1項目（最大20点）を採点し、スコアとフィードバック文を返す。"""
    low, high = target_range
    if low <= value <= high:
        return 20, f"✅ {label}（{value}）: 理想的な配合です！（+20点）"

    distance = low - value if value < low else value - high
    direction = "控えめすぎ" if value < low else "強すぎ"
    if distance <= TOLERANCE:
        return 10, f"🔺 {label}（{value}）: わずかに{direction}ですが許容範囲内です。（+10点）"

    return 0, f"❌ {label}（{value}）: 客の好みから大きく外れています（{direction}）。（+0点）"


def _score_method(selected_method: str, preferred_method: str) -> tuple[int, str]:
    """調理法（最大20点）を採点し、スコアとフィードバック文を返す。"""
    if selected_method == preferred_method:
        return 20, f"✅ 調理法（{selected_method}）: 完璧な仕上げ方です！（+20点）"
    return 0, f"❌ 調理法（{selected_method}）: この客の注文には合っていませんでした。（+0点）"


def _score_spell(input_spell: str, target_keywords: list[str]) -> tuple[int, str]:
    """呪文 / キーワード（最大20点・複数の類義語許容）を採点し、スコアとフィードバック文を返す。"""
    normalized_input = input_spell.strip().upper()
    normalized_targets = [kw.strip().upper() for kw in target_keywords if kw.strip()]

    if not normalized_input:
        return 0, "❌ 刻印呪文（未入力）: 魔力が込められていません。（+0点）"

    if normalized_input in normalized_targets:
        return 20, f"✅ 刻印呪文（{input_spell.strip()}）: 真の言霊が完璧に共鳴しました！（+20点）"

    if any(
        target in normalized_input or normalized_input in target
        for target in normalized_targets
    ):
        return 10, f"🔺 刻印呪文（{input_spell.strip()}）: 言霊の片鱗は感じられますが不完全です。（+10点）"

    return 0, f"❌ 刻印呪文（{input_spell.strip()}）: 呪文が不発に終わりました。（+0点）"


def _determine_stage_rank(score: int) -> tuple[str, str]:
    """ステージ得点（0〜100）から内部ランクキーと表示ランク名を返す。"""
    if score >= 85:
        return "perfect", "Perfect"
    if score >= 60:
        return "good", "Good"
    return "bad", "Bad"


def evaluate_concoction(
    stage: StageData,
    sweetness: int,
    bitterness: int,
    spiciness: int,
    method: str,
    spell: str,
) -> dict[str, Any]:
    """プレイヤーの調合内容を最大100点満点で採点し、評価結果辞書を生成する。"""
    req = stage["requirements"]

    sweet_score, sweet_msg = _score_ingredient("甘味", sweetness, req["sweetness_range"])
    bitter_score, bitter_msg = _score_ingredient("苦味", bitterness, req["bitterness_range"])
    spicy_score, spicy_msg = _score_ingredient("刺激", spiciness, req["spiciness_range"])
    method_score, method_msg = _score_method(method, req["preferred_method"])
    valid_spells = [req["spell_keyword"], *req.get("spell_aliases", [])]
    spell_score, spell_msg = _score_spell(spell, valid_spells)

    ingredient_total = sweet_score + bitter_score + spicy_score
    total_score = ingredient_total + method_score + spell_score

    rank_key, rank_label = _determine_stage_rank(total_score)
    reaction = stage["reactions"][rank_key]  # type: ignore[literal-required]

    return {
        "stage_id": stage["id"],
        "pattern_id": stage.get("pattern_id", ""),
        "pattern_title": stage.get("pattern_title", ""),
        "stage_name": stage["name"],
        "avatar": stage["avatar"],
        "image": stage.get("image", ""),
        "score": total_score,
        "rank_key": rank_key,
        "rank_label": rank_label,
        "reaction": reaction,
        "inputs": {
            "sweetness": sweetness,
            "bitterness": bitterness,
            "spiciness": spiciness,
            "method": method,
            "spell": spell.strip(),
        },
        "breakdown": {
            "sweetness": sweet_score,
            "bitterness": bitter_score,
            "spiciness": spiciness,
            "ingredients_total": ingredient_total,
            "method": method_score,
            "spell": spell_score,
        },
        "feedback_messages": [
            sweet_msg,
            bitter_msg,
            spicy_msg,
            method_msg,
            spell_msg,
        ],
    }


def evaluate_final_rank(total_score: int) -> dict[str, str]:
    """全3ステージ累積スコア（0〜300点）から総合ランクと称号を返す。"""
    if total_score >= 260:
        return {
            "rank": "S",
            "title": "三ツ星ゴーストパティシエ",
            "image": "assets/chef_rank_s.jpg",
            "description": "冥界中にその名を轟かせる伝説の菓子職人！今夜も怪異たちは至福の笑顔で成仏していきました。",
            "effect": "balloons",
        }
    if total_score >= 180:
        return {
            "rank": "A",
            "title": "一人前の怪異菓子職人",
            "image": "assets/chef_rank_a.jpg",
            "description": "怪異たちの舌をしっかりと満足させる確かな腕前。真夜中の行列が絶えない人気店です！",
            "effect": "snow",
        }
    if total_score >= 100:
        return {
            "rank": "B",
            "title": "見習い悪魔の厨房係",
            "image": "assets/chef_rank_b.jpg",
            "description": "まだまだ修行の余地あり。魔導書を読み返し、客の声に耳を傾ければさらに腕が上がるはず！",
            "effect": "none",
        }
    return {
        "rank": "C",
        "title": "厨房爆破の常習犯",
        "image": "assets/chef_rank_c.jpg",
        "description": "オーブンからは黒煙が上がり、怪異たちは逃げ出してしまった…！まずは魔導書の基本から復習しよう。",
        "effect": "none",
    }

