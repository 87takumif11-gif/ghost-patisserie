"""ステージデータ・モンスターセリフ・正解定義モジュール。

各キャラクターごとに3種類の調合パターン（計9パターン）を定義し、
ゲーム開始ごとに各キャラクターからランダムで1パターンずつ選出する。
"""

from __future__ import annotations

import random
from typing import Final, TypedDict


class StageRequirements(TypedDict):
    sweetness_range: tuple[int, int]
    bitterness_range: tuple[int, int]
    spiciness_range: tuple[int, int]
    preferred_method: str
    spell_keyword: str
    spell_aliases: list[str]


class StageReactions(TypedDict):
    perfect: str
    good: str
    bad: str


class StageData(TypedDict):
    id: int
    pattern_id: str
    pattern_title: str
    name: str
    avatar: str
    image: str
    story: str
    hint: str
    requirements: StageRequirements
    reactions: StageReactions


COOKING_METHODS: Final[list[str]] = [
    "暗闇霊気熟成",
    "怨念直火焼き",
    "絶対零度冷却",
]

CHARACTER_STAGE_POOLS: Final[list[list[StageData]]] = [
    # 第1夜: 彷徨うジャック・オー・ランタン（3パターン）
    [
        {
            "id": 1,
            "pattern_id": "1-A",
            "pattern_title": "消えかけの灯火",
            "name": "彷徨うジャック・オー・ランタン",
            "avatar": "🎃",
            "image": "assets/stage1_jack.jpg",
            "story": "「頭の火が消えそうだ…芯から温まる、甘くて香ばしいパイをくれ…！」",
            "hint": "たっぷり濃厚な強い甘味が好みで、苦味は控えめに抑えるのがコツ。体が温まるよう刺激もほどよく効かせよう。冷たいものは厳禁、火で仕上げること。合言葉はハロウィンの定番の『ごちそう』だ。",
            "requirements": {
                "sweetness_range": (70, 100),
                "bitterness_range": (0, 30),
                "spiciness_range": (40, 80),
                "preferred_method": "怨念直火焼き",
                "spell_keyword": "TREAT",
                "spell_aliases": ["TREATS", "FEAST", "SWEETS"],
            },
            "reactions": {
                "perfect": "「カッカッカ！炎が燃え盛るようだ！最高のハロウィンだな！」",
                "good": "「悪くない…火種はなんとか保てそうだ。」",
                "bad": "「冷え切って火が消えちまったじゃねえか…！（消滅）」",
            },
        },
        {
            "id": 1,
            "pattern_id": "1-B",
            "pattern_title": "燃えすぎたカボチャ頭",
            "name": "彷徨うジャック・オー・ランタン",
            "avatar": "🎃",
            "image": "assets/stage1_jack.jpg",
            "story": "「アチチッ！今度は頭の炎が燃えすぎて焦げちまいそうだ！甘くてヒンヤリ冷たいデザートで頭を冷やしてくれ！」",
            "hint": "しっかり濃厚な強い甘味で癒やしつつ、苦味と刺激はどちらもほんのわずかに抑えて優しく仕上げよう。火は絶対に使わず、凍てつく冷気で一気に冷やすこと。合言葉は火照った頭を冷やす冷たい『氷』だ。",
            "requirements": {
                "sweetness_range": (70, 100),
                "bitterness_range": (0, 25),
                "spiciness_range": (0, 25),
                "preferred_method": "絶対零度冷却",
                "spell_keyword": "ICE",
                "spell_aliases": ["COLD", "COOL", "FROST", "FREEZE"],
            },
            "reactions": {
                "perfect": "「ふぅ〜っ！生き返るぜ！甘くてキンキンで最高の気分だ！」",
                "good": "「おお、だいぶ熱が引いてきたぞ。助かったぜ！」",
                "bad": "「ギャーッ！余計に頭が燃え上がっちまったじゃねえか！（炎上）」",
            },
        },
        {
            "id": 1,
            "pattern_id": "1-C",
            "pattern_title": "長い夜道のランタン",
            "name": "彷徨うジャック・オー・ランタン",
            "avatar": "🎃",
            "image": "assets/stage1_jack.jpg",
            "story": "「今夜は朝まで墓場を歩き回るんだ。甘すぎず、じんわり苦味とスパイスが効いた大人な熟成菓子を頼むぜ。」",
            "hint": "甘味は真ん中より控えめに抑え、代わりにしっかり強い苦味とピリッと強い刺激の両方を効かせよう。調理は火も氷も使わず、夜の霊気にさらしてじっくり馴染ませること。合言葉は夜空にぽっかり浮かぶ丸い『月』だ。",
            "requirements": {
                "sweetness_range": (20, 45),
                "bitterness_range": (65, 95),
                "spiciness_range": (65, 95),
                "preferred_method": "暗闇霊気熟成",
                "spell_keyword": "MOON",
                "spell_aliases": ["FULL MOON", "FULLMOON", "LUNA"],
            },
            "reactions": {
                "perfect": "「これだよこれ！月夜の散歩にぴったりの渋くて深い味わいだ！」",
                "good": "「なかなかの味だな。夜明けまで歩けそうだぜ。」",
                "bad": "「うーん、これじゃあ夜道を歩く元気が出ねえなぁ…。」",
            },
        },
    ],
    # 第2夜: 夜想の吸血鬼伯爵（3パターン）
    [
        {
            "id": 2,
            "pattern_id": "2-A",
            "pattern_title": "冷徹なる貴族の晩餐",
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
                "spell_aliases": ["BATS", "VAMPIRE BAT"],
            },
            "reactions": {
                "perfect": "「ブラボー…！氷のように冷徹で、高貴な苦味だ。気に入ったよ。」",
                "good": "「まあ合格点だ。喉の渇きは癒えた。」",
                "bad": "「ぬるい！そして甘ったるい！私の舌を侮辱する気か！」",
            },
        },
        {
            "id": 2,
            "pattern_id": "2-B",
            "pattern_title": "百年の目覚めの一皿",
            "name": "夜想の吸血鬼伯爵",
            "avatar": "🧛‍♂️",
            "image": "assets/stage2_vampire.jpg",
            "story": "「百年の眠りから目覚めたばかりでな…凍えた血が沸き立つような、熱く情熱的な刺激と芳醇な甘美さを求めている。」",
            "hint": "眠りから覚ますため、甘味も刺激もどちらもたっぷりと強く効かせよう。苦味は真ん中あたりに整えると気品が出る。仕上げは業火で熱々に焼き上げること。合言葉は吸血鬼の瞳のように鮮やかな色の『赤』だ。",
            "requirements": {
                "sweetness_range": (70, 95),
                "bitterness_range": (35, 60),
                "spiciness_range": (70, 100),
                "preferred_method": "怨念直火焼き",
                "spell_keyword": "RED",
                "spell_aliases": ["CRIMSON", "SCARLET", "RUBY", "BLOOD"],
            },
            "reactions": {
                "perfect": "「素晴らしい…！冷え切った血管に情熱の炎が巡っていくようだ！」",
                "good": "「ふむ、悪くない目覚めの一皿だ。礼を言おう。」",
                "bad": "「これでは二度寝してしまいそうだ…やり直したまえ！」",
            },
        },
        {
            "id": 2,
            "pattern_id": "2-C",
            "pattern_title": "古城の仮面舞踏会",
            "name": "夜想の吸血鬼伯爵",
            "avatar": "🧛‍♂️",
            "image": "assets/stage2_vampire.jpg",
            "story": "「今宵は我が城で舞踏会がある。極端な味付けは避け、甘味も苦味も気品よく調和した熟成菓子を用意したまえ。」",
            "hint": "甘味と苦味はどちらも強すぎず弱すぎず、真ん中あたりで気品よく調和させよう。舞踏会の客が驚かないよう刺激はほんのわずかに抑えること。火も氷も使わず、夜の霊気にさらして静かに熟成させよ。合言葉は太陽を嫌う吸血鬼が愛する『暗い（暗闇）』を表す英単語だ。",
            "requirements": {
                "sweetness_range": (40, 65),
                "bitterness_range": (40, 65),
                "spiciness_range": (0, 20),
                "preferred_method": "暗闇霊気熟成",
                "spell_keyword": "DARK",
                "spell_aliases": ["DARKNESS", "SHADOW", "NIGHT", "GLOOM"],
            },
            "reactions": {
                "perfect": "「見事な調和だ…！今宵の舞踏会の主役にふさわしい至高の銘菓だよ。」",
                "good": "「まずまずの気品だな。客人に振る舞うとしよう。」",
                "bad": "「なんという無作法な味だ！舞踏会が台無しではないか！」",
            },
        },
    ],
    # 第3夜: 迷子のレイス少女（3パターン）
    [
        {
            "id": 3,
            "pattern_id": "3-A",
            "pattern_title": "お祭りの夜の記憶",
            "name": "迷子のレイス少女",
            "avatar": "👻",
            "image": "assets/stage3_wraith.jpg",
            "story": "「私…生前の記憶がなくて…。ピリッと刺激があって、いたずらっぽい味のお菓子を食べたら思い出せるかも…？」",
            "hint": "目が覚めるほど強烈な刺激が好み！甘味と苦味はどちらも強すぎず、真ん中より少し控えめなあたりで絶妙に釣り合わせよう。調理は火も氷も使わず霊気にさらして馴染ませ、合言葉はお菓子をくれなきゃ仕掛けるハロウィンの『いたずら』だ。",
            "requirements": {
                "sweetness_range": (30, 50),
                "bitterness_range": (30, 50),
                "spiciness_range": (80, 100),
                "preferred_method": "暗闇霊気熟成",
                "spell_keyword": "TRICK",
                "spell_aliases": ["TRICKS", "PRANK", "MISCHIEF"],
            },
            "reactions": {
                "perfect": "「わぁっ！電気が走ったみたい！…あのお祭りの日のことを思い出したわ！」",
                "good": "「舌がピリピリして面白い…少しだけ何か思い出せそう。」",
                "bad": "「うぅ…何も感じない…体が透けて消えちゃいそう…。」",
            },
        },
        {
            "id": 3,
            "pattern_id": "3-B",
            "pattern_title": "懐かしいお家の香り",
            "name": "迷子のレイス少女",
            "avatar": "👻",
            "image": "assets/stage3_wraith.jpg",
            "story": "「なんだか胸の奥が寂しいの…。昔お家で食べたみたいな、焼きたてで甘くて優しい味のお菓子が食べたいな…。」",
            "hint": "心を包み込むようなとても強い甘味にして、苦味と刺激はどちらもほんのわずかに抑えた優しい味にしよう。オーブンの火で温かく焼き上げること。合言葉は迷子の彼女がずっと帰りたがっている温かい『家』だ。",
            "requirements": {
                "sweetness_range": (75, 100),
                "bitterness_range": (0, 20),
                "spiciness_range": (0, 20),
                "preferred_method": "怨念直火焼き",
                "spell_keyword": "HOME",
                "spell_aliases": ["HOUSE", "MY HOME", "SWEET HOME"],
            },
            "reactions": {
                "perfect": "「ぽかぽかして甘い…！思い出した…私の帰るお家は、いつもこの香りがしたわ！」",
                "good": "「あたたかくて優しい味…なんだか涙が出そうになるわ。」",
                "bad": "「うぅっ、苦くてびっくりしちゃった…お家の味じゃなかったみたい…。」",
            },
        },
        {
            "id": 3,
            "pattern_id": "3-C",
            "pattern_title": "初雪の日の約束",
            "name": "迷子のレイス少女",
            "avatar": "👻",
            "image": "assets/stage3_wraith.jpg",
            "story": "「雪が降る日に、誰かと冷たくてちょっぴり大人な味のお菓子を分け合った気がするの…どんな味だったかしら…？」",
            "hint": "甘味は真ん中あたりに整えつつ、ちょっぴり背伸びした強い苦味と、スッと爽やかに広がる中くらいの刺激を合わせよう。仕上げは氷点下の冷気でしっかり凍らせること。合言葉は冬の空から舞い降りる白い『雪』だ。",
            "requirements": {
                "sweetness_range": (40, 65),
                "bitterness_range": (65, 90),
                "spiciness_range": (40, 65),
                "preferred_method": "絶対零度冷却",
                "spell_keyword": "SNOW",
                "spell_aliases": ["SNOWY", "SNOWFLAKE", "WHITE SNOW"],
            },
            "reactions": {
                "perfect": "「これよ！冷たくてほろ苦い雪の日の味…！あの人との約束、全部思い出したわ！」",
                "good": "「ひんやりして素敵な味ね…記憶の霧が少しずつ晴れていくわ。」",
                "bad": "「ちがう…これじゃ記憶がまた遠くへ消えていっちゃう…！」",
            },
        },
    ],
]

# デフォルトの代表ステージ配列（後方互換用）
STAGES: Final[list[StageData]] = [pool[0] for pool in CHARACTER_STAGE_POOLS]


def select_random_stages() -> list[StageData]:
    """各キャラクターの3パターンからランダムに1つずつ選出し、全3ステージの配列を返す。"""
    return [random.choice(pool) for pool in CHARACTER_STAGE_POOLS]
