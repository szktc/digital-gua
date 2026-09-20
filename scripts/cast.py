#!/usr/bin/env python3
"""数字卦起卦脚本。

用法:
    python cast.py 123 456 789
    python cast.py 123 456 789 --order upper-first
    python cast.py --lookup 水雷屯
    python cast.py --lookup 3

三数起卦规则(傅佩荣数字卦法, 默认):
    第一组 % 8 -> 下卦
    第二组 % 8 -> 上卦
    第三组 % 6 -> 动爻
    余数 0: %8 记为 8(坤), %6 记为 6(上爻)
    先天八卦数: 乾1 兑2 离3 震4 巽5 坎6 艮7 坤8

脚本只做确定性计算和查表, 输出 JSON, 解读交给模型。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "references" / "hexagrams.json"

# 先天八卦: 数 -> 名; 二进制自下而上, 1 阳 0 阴
TRIGRAM_BY_NUM = {
    1: ("乾", "111", "天"),
    2: ("兑", "110", "泽"),
    3: ("离", "101", "火"),
    4: ("震", "100", "雷"),
    5: ("巽", "011", "风"),
    6: ("坎", "010", "水"),
    7: ("艮", "001", "山"),
    8: ("坤", "000", "地"),
}
TRIGRAM_BY_NAME = {v[0]: (k, v[1], v[2]) for k, v in TRIGRAM_BY_NUM.items()}
TRIGRAM_BY_BIN = {v[1]: v[0] for v in TRIGRAM_BY_NUM.values()}
LINE_NAMES = ["初", "二", "三", "四", "五", "上"]


def load_data() -> dict:
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def build_index(data: dict):
    by_name = {}
    by_bin = {}
    by_number = {}
    for h in data["hexagrams"]:
        lower_bin = TRIGRAM_BY_NAME[h["lower"]][1]
        upper_bin = TRIGRAM_BY_NAME[h["upper"]][1]
        h["binary"] = lower_bin + upper_bin  # 自下而上六位
        by_name[h["name"]] = h
        by_name[h["full_name"]] = h
        by_bin[h["binary"]] = h
        by_number[h["number"]] = h
    return by_name, by_bin, by_number


def mod_or_max(n: int, m: int) -> int:
    r = n % m
    return m if r == 0 else r


def hexagram_view(h: dict, moving: int | None = None) -> dict:
    view = {
        "number": h["number"],
        "name": h["name"],
        "full_name": h["full_name"],
        "upper": h["upper"],
        "lower": h["lower"],
        "binary_bottom_to_top": h["binary"],
        "judgement": h["judgement"],
        "image": h["image"],
    }
    if moving is not None:
        view["moving_line_text"] = h["lines"][moving - 1]
    return view


def cast(n1: int, n2: int, n3: int, order: str, data: dict) -> dict:
    by_name, by_bin, by_number = build_index(data)

    a = mod_or_max(n1, 8)
    b = mod_or_max(n2, 8)
    moving = mod_or_max(n3, 6)

    if order == "lower-first":
        lower_num, upper_num = a, b
    else:
        upper_num, lower_num = a, b

    lower_name, lower_bin, _ = TRIGRAM_BY_NUM[lower_num]
    upper_name, upper_bin, _ = TRIGRAM_BY_NUM[upper_num]

    ben_bin = lower_bin + upper_bin
    ben = by_bin[ben_bin]

    # 变卦: 翻转动爻
    bits = list(ben_bin)
    bits[moving - 1] = "0" if bits[moving - 1] == "1" else "1"
    bian = by_bin["".join(bits)]

    # 互卦: 2,3,4 爻为下卦, 3,4,5 爻为上卦
    hu_bin = ben_bin[1:4] + ben_bin[2:5]
    hu = by_bin[hu_bin]

    # 错卦: 六爻全反
    cuo = by_bin["".join("0" if c == "1" else "1" for c in ben_bin)]
    # 综卦: 上下颠倒
    zong = by_bin[ben_bin[::-1]]

    line_yang = ben_bin[moving - 1] == "1"
    moving_label = ("九" if line_yang else "六")
    if moving == 1:
        moving_name = "初" + moving_label
    elif moving == 6:
        moving_name = "上" + moving_label
    else:
        moving_name = moving_label + LINE_NAMES[moving - 1]

    # 校验: 用本卦名反查上下卦
    check_ok = (ben["upper"] == upper_name and ben["lower"] == lower_name
                and bian["binary"] != ben_bin)

    return {
        "input": {"numbers": [n1, n2, n3], "order": order},
        "steps": {
            "first_mod_8": a,
            "second_mod_8": b,
            "third_mod_6": moving,
            "lower_trigram": f"{lower_name}({lower_num})",
            "upper_trigram": f"{upper_name}({upper_num})",
            "moving_line": moving,
        },
        "check": {
            "ok": check_ok,
            "detail": (
                f"上{upper_name}下{lower_name} -> {ben['full_name']}; "
                f"反查 {ben['name']} 上卦={ben['upper']} 下卦={ben['lower']}; "
                f"动{moving_name} -> {bian['full_name']}"
            ),
        },
        "moving_line_name": moving_name,
        "ben_gua": hexagram_view(ben, moving),
        "bian_gua": hexagram_view(bian),
        "hu_gua": hexagram_view(hu),
        "cuo_gua": {"name": cuo["full_name"], "number": cuo["number"]},
        "zong_gua": {"name": zong["full_name"], "number": zong["number"]},
        "all_lines_of_ben_gua": ben["lines"],
        "extra_of_ben_gua": ben.get("extra"),
    }


def lookup(key: str, data: dict) -> dict:
    by_name, by_bin, by_number = build_index(data)
    h = None
    if key.isdigit():
        h = by_number.get(int(key))
    if h is None:
        h = by_name.get(key)
    if h is None:
        raise SystemExit(f"未找到卦: {key}")
    out = hexagram_view(h)
    out["lines"] = h["lines"]
    if h.get("extra"):
        out["extra"] = h["extra"]
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="数字卦起卦(输出 JSON)")
    p.add_argument("numbers", nargs="*", type=int, help="三个正整数")
    p.add_argument("--order", choices=["lower-first", "upper-first"],
                   default="lower-first",
                   help="第一组数定下卦(默认, 傅佩荣法)还是定上卦")
    p.add_argument("--lookup", help="按卦名或序号查卦, 如 水雷屯 / 屯 / 3")
    args = p.parse_args(argv)

    data = load_data()

    if args.lookup:
        result = lookup(args.lookup, data)
    else:
        if len(args.numbers) != 3:
            p.error("需要三个正整数, 例如: cast.py 123 456 789")
        if any(n <= 0 for n in args.numbers):
            p.error("数字必须为正整数")
        result = cast(*args.numbers, order=args.order, data=data)

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
