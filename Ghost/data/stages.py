"""ステージデータ・モンスターセリフ・正解定義モジュール。"""

from __future__ import annotations

from typing import Final, TypedDict


class StageRequirements(TypedDict):
    sweetness_range: tuple[int, int]
    bitterness_range: tuple[int, int]
    spiciness_range: tuple[int, int]
    preferred_method: str
    spell_keyword: str


class StageReactions(TypedDict):
    perfect: str
    good: str
    bad: str


class StageData(TypedDict):
    id: int
    name: str
    avatar: str
    image: str
    story: str
    hint: str
    requirements: StageRequirements
    reactions: StageReactions


COOKING_METHODS: Final[list[str]] = [
    "常温放置熟成",
    "怨念直火焼き",
    "絶対零度冷却",
]

STAGES: Final[list[StageData]] = [
    {
        "id": 1,
        "name": "彷徨うジャック・オー・ランタン",
        "avatar": "🎃",
        "image": "assets/stage1_jack.jpg",
        "story": "「頭の火が消えそうだ…芯から温まる、甘くて香ばしいパイをくれ…！」",
        "hint": "たっぷり濃厚な強い甘味が好みで、苦味は控えめに抑えるのがコツ。体が温まるよう刺激もほどよく効かせよう。冷たいものは厳禁、火で仕上げること。合言葉はハロウィンの定番の『ごちそう』だ。",
        "requirements": {
            "sweetness_range": (70, 100),    # 甘味
            "bitterness_range": (0, 30),     # 苦味
            "spiciness_range": (40, 80),     # 刺激
            "preferred_method": "怨念直火焼き",
            "spell_keyword": "TREAT",
        },
        "reactions": {
            "perfect": "「カッカッカ！炎が燃え盛るようだ！最高のハロウィンだな！」",
            "good": "「悪くない…火種はなんとか保てそうだ。」",
            "bad": "「冷え切って火が消えちまったじゃねえか…！（消滅）」",
        },
    },
    {
        "id": 2,
        "name": "夜想の吸血鬼伯爵",
        "avatar": "🧛‍♂️",
        "image": "assets/stage2_vampire.jpg",
        "story": "「下品な甘さは不要だ。深く熟成された苦味と、喉を刺す冷気を感じるデザートを所望する。」",
        "hint": "深く重厚な強い苦味を好む一方、甘味はほんのわずかに抑えること。刺激も控えめにして上品にまとめよう。絶対に熱を通さず凍てつくほど冷やすこと。合言葉は夜を裂くあの羽音…吸血鬼が姿を借りる『黒き翼の生き物』だ。",
        "requirements": {
            "sweetness_range": (0, 20),
            "bitterness_range": (60, 90),
            "spiciness_range": (0, 40),
            "preferred_method": "絶対零度冷却",
            "spell_keyword": "BAT",
        },
        "reactions": {
            "perfect": "「ブラボー…！氷のように冷徹で、高貴な苦味だ。気に入ったよ。」",
            "good": "「まあ合格点だ。喉の渇きは癒えた。」",
            "bad": "「ぬるい！そして甘ったるい！私の舌を侮辱する気か！」",
        },
    },
    {
        "id": 3,
        "name": "迷子のレイス少女",
        "avatar": "👻",
        "image": "assets/stage3_wraith.jpg",
        "story": "「私…生前の記憶がなくて…。ピリッと刺激があって、いたずらっぽい味のお菓子を食べたら思い出せるかも…？」",
        "hint": "目が覚めるほど強烈な刺激が好み！甘味と苦味はどちらも強すぎず、真ん中より少し控えめなあたりで絶妙に釣り合わせよう。調理は常温で馴染ませ、合言葉はお菓子をくれなきゃ仕掛けるハロウィンの『いたずら』だ。",
        "requirements": {
            "sweetness_range": (30, 50),
            "bitterness_range": (30, 50),
            "spiciness_range": (80, 100),
            "preferred_method": "常温放置熟成",
            "spell_keyword": "TRICK",
        },
        "reactions": {
            "perfect": "「わぁっ！電気が走ったみたい！…あのお祭りの日のことを思い出したわ！」",
            "good": "「舌がピリピリして面白い…少しだけ何か思い出せそう。」",
            "bad": "「うぅ…何も感じない…体が透けて消えちゃいそう…。」",
        },
    },
]

