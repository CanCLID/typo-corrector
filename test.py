from rules import apply_contextual_rules
import re

regular_typos = []

# Read regular typos
for line in open("./regular.txt", "r", encoding="utf-8"):
    typo, replace = line.strip().split(",")
    regular_typos.append(
        (re.compile(typo.replace(" ", "\s*"), re.I), replace))

def fix_regular_typo(line: str) -> str:
    """
    Regular typo means that they can be simply replaced by a regular expression.
    Fixing them does not require any context information.
    """
    for typo, replace in regular_typos:
        line = typo.sub(replace, line)
    return line

def correct(line):
    stripped_line = line.strip()
    fixed = fix_regular_typo(stripped_line)
    fixed = apply_contextual_rules(fixed)

    return fixed

def test_即係():
    # 遮
    assert correct("遮係噉") == "即係噉"
    assert correct("哪！遮係噉") == "哪！即係噉"
    assert correct("落雨要擔遮係嗎？") == "落雨要擔遮係嗎？"
    assert correct("落雨要把遮係嗎？") == "落雨要把遮係嗎？"
    assert correct("落雨要收遮係嗎？") == "落雨要收遮係嗎？"
    assert correct("落雨要雨遮係嗎？") == "落雨要雨遮係嗎？"

    # 姐
    assert correct("姐係噉") == "即係噉"
    assert correct("哪！姐係噉") == "哪！即係噉"
    assert correct("我家姐係我親人") == "我家姐係我親人"
    assert correct("我表姐係我親人") == "我表姐係我親人"
    assert correct("我堂姐係我親人") == "我堂姐係我親人"
    assert correct("我契姐係我親人") == "我契姐係我親人"
    assert correct("我姐姐係我親人") == "我姐姐係我親人"
    assert correct("我姑姐係我親人") == "我姑姐係我親人"
    assert correct("我小姐係我親人") == "我小姐係我親人"

if __name__ == "__main__":
    test_即係()