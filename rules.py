from __future__ import annotations

import re
from typing import Callable

import pycantonese

han = r"\u3006\u3007\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002ebef\U00030000-\U000323af"
full_width_punct = r"\uff00-\uffef"
cjk_punct = r"\u3000-\u303f"
kana = r"\u3040-\u309f\u30a0-\u30ff\u31f0-\u31ff"
hangul = r"\uac00-\ud7af\u1100-\u11ff"

cjk_regex = f"[{han}{full_width_punct}{cjk_punct}{kana}{hangul}]"
cjk_pattern = re.compile(rf"(?<={cjk_regex})\s+(?={cjk_regex})")
number_pattern = re.compile(r"(?<={num})\s+(?={num})".format(num=r"[\d.,]"))

zo_words = ["左側", "左右", "左邊", "左手", "左腳", "左方"]


class Context:
    pos_list: list[tuple[str, str]]
    i: int
    word: str
    pos: str
    next_word: str = ""
    next_pos: str = ""
    prev_word: str = ""
    prev_pos: str = ""

    @property
    def sentence_remain(self):
        """The remaining part of the sentence."""
        return "".join(x[0] for x in self.pos_list[self.i:])

    def replace_word(self, word: str):
        self.pos_list[self.i] = word, self.pos_list[self.i][1]


class Pos:
    NONE = ""
    NOUN = "NOUN"
    VERB = "VERB"
    PRON = "PRON"
    PROPN = "PROPN"
    ADJ = "ADJ"
    ADP = "ADP"
    ADV = "ADV"
    AUX = "AUX"
    PART = "PART"
    X = "X"


_handlers: dict[str, Callable[[Context], None]] = {}


def segment_line(line: str) -> list[str]:
    words = []
    segments = re.split(r"\s+", line)
    for seg in segments:
        words += pycantonese.segment(seg)
    return words


def fix_space(line: str) -> str:
    """Remove spaces between Han characters and non-Han characters."""
    line = cjk_pattern.sub("", line)
    return number_pattern.sub("", line)


# Debugging purpose
# pos_file = open("pos.txt", "w", encoding="utf-8")


def apply_contextual_rules(line: str):
    ctx = Context()
    ctx.pos_list = pycantonese.pos_tag(segment_line(line))

    # Debugging purpose
    # print(ctx.pos_list, file=pos_file)

    for ctx.i, (ctx.word, ctx.pos) in enumerate(ctx.pos_list):
        if ctx.i + 1 < len(ctx.pos_list):
            ctx.next_word, ctx.next_pos = ctx.pos_list[ctx.i + 1]
        else:
            ctx.next_word, ctx.next_pos = "", Pos.NONE

        rule_handler = _handlers.get(ctx.word, None)
        if rule_handler:
            # If the word triggers a rule, apply the rule
            rule_handler(ctx)
        # Some rules can't be triggered by the decorator, so we put them here
        elif "左" in ctx.word and ctx.word not in zo_words:
            if ctx.prev_pos == Pos.VERB:
                ctx.pos_list[ctx.i] = ctx.word.replace(
                    "左", "咗"), ctx.pos_list[ctx.i][1]

        ctx.prev_word = ctx.word
        ctx.prev_pos = ctx.pos

    return fix_space(" ".join(w for w, _ in ctx.pos_list))


def contextual_rule(word: str, pos: set[str] = set()):
    """Decorator for registering a contextual typo correction rule."""

    def deco(f):
        if word in _handlers:
            raise ValueError(
                f"rule for {word} already exists: {_handlers[word]}")
        _handlers[word] = f
        return f
    return deco


@contextual_rule("比")
def _(c: Context):
    """
    比 -> 畀: 如果後面第一個詞係名詞，且第二個詞係形容詞、副詞，就係 比
    """
    remain_words, remain_pos = zip(*c.pos_list[c.i:])
    if "仲" in remain_words or "更" in remain_words or Pos.ADJ in remain_pos or Pos.ADV in remain_pos:
        return
    c.replace_word("畀")


# @contextual_rule("俾")
# def _(c: Context):
#     if c.next_word not in ("使", "能", "便", "斯麥", "路支"):
#         c.replace_word("畀")


@contextual_rule("d")
@contextual_rule("D")
def _(c: Context):
    if re.search(cjk_regex, c.next_word) or c.prev_pos in (Pos.ADJ, Pos.ADV):
        c.replace_word("啲")


@contextual_rule("番")
def _(c: Context):
    if c.prev_pos == Pos.VERB:
        c.replace_word("返")


@contextual_rule("黎")
def _(c: Context):
    """黎 -> 嚟
    如果 黎 字係動詞，就改成 嚟.
    """
    if c.pos == Pos.VERB or c.next_pos == Pos.VERB:
        c.replace_word("嚟")


# @contextual_rule("咁")
# def _(c: Context):
#     """咁 -> 噉
#     如果前面係形容詞、副詞，或者後面後動詞、名詞、代詞，就係 噉
#     """
#     # 句末直接當 噉
#     if c.next_word == "":
#         c.replace_word("噉")
#     elif c.next_pos in (Pos.ADJ, Pos.ADV):
#         return
#     if (c.next_pos in (Pos.VERB, Pos.NOUN, Pos.PRON, Pos.PART, Pos.AUX) or
#             c.prev_pos in (Pos.ADJ, Pos.ADV, Pos.NOUN)):
#         c.replace_word("噉")


@contextual_rule("甘")
def _(c: Context):
    """甘 -> 咁/噉
    如果前面係形容詞、副詞，或者後面後動詞、名詞、代詞，就係 噉.
    如果後面係形容詞、副詞，就係 咁
    """
    if c.pos in (Pos.VERB, Pos.NOUN):
        return
    # 句末直接當噉
    if c.next_word == "":
        c.replace_word("噉")
    elif c.next_pos in (Pos.ADV, Pos.ADJ):
        c.replace_word("咁")
        return
    if (c.next_pos in (Pos.VERB, Pos.NOUN, Pos.PRON, Pos.PART, Pos.AUX) or
            c.prev_pos in (Pos.ADJ, Pos.ADV, Pos.NOUN)):
        c.replace_word("噉")


@contextual_rule("既")
def _(c: Context):
    """既 -> 嘅
    如果 既 字前面係一個名詞/動詞/形容詞/副詞，句子後面又冇"又 ADV/ADJ/VERB"嘅結構，噉就改成 嘅.
    """
    if c.prev_pos not in (Pos.PROPN, Pos.PRON, Pos.NOUN, Pos.ADJ, Pos.ADV, Pos.VERB):
        return
    # 句子後面冇 "又 ADV/ADJ/VERB" 嘅結構
    if "又" in c.sentence_remain and c.next_pos not in (Pos.ADJ, Pos.ADV, Pos.VERB):
        return
    c.replace_word("嘅")


@contextual_rule("果")
def _(c: Context):
    """果 -> 嗰"""
    if c.next_pos == Pos.NOUN:
        c.replace_word("嗰")


@contextual_rule("野")
def _(c: Context):
    """野 -> 嘢
    如果係隻名詞，就改成 嘢. 包埋動詞同X係因為 pycantonese 有時會識別成動詞.
    """
    if c.pos in (Pos.PRON, Pos.NOUN, Pos.X, Pos.AUX) or c.prev_pos == Pos.VERB:
        c.replace_word("嘢")


@contextual_rule("無")
def _(c: Context):
    """無 -> 冇"""
    if c.next_pos in (Pos.NOUN, Pos.ADP):
        c.replace_word("冇")


@contextual_rule("曬")
def _(c: Context):
    """曬 -> 晒"""
    if c.pos == Pos.VERB:
        c.replace_word("晒")


@contextual_rule("哂")
def _(c: Context):
    """哂 -> 晒"""
    if c.next_word != "笑":
        c.replace_word("晒")


@contextual_rule("左")
def _(c: Context):
    """左 -> 咗: 如果 左 字前面係一個動詞，噉就改成 咗."""
    if c.prev_pos in (Pos.VERB, Pos.ADJ, Pos.ADV):
        c.replace_word("咗")


@contextual_rule("著")
def _(c: Context):
    """著 -> 着: 如果 著 字前面係一個動詞，噉就改成 住."""
    if c.pos == Pos.VERB:
        c.replace_word("着")
    elif c.prev_pos == Pos.VERB:
        c.replace_word("住")
