# 粵文錯別字修正器

[![license](https://img.shields.io/github/license/DAVFoundation/captain-n3m0.svg?style=flat-square)](https://github.com/DAVFoundation/captain-n3m0/blob/master/LICENSE)

呢個係隻粵文錯別字修正器，會自動改正常見嘅粵文錯別字。

本修正器採用嘅正字法見 [粵文常見錯別字](https://jyutping.org/blog/typo/)

## 依賴

- Python >= 3.9
- PyCantonese

## 用法

隻修正器可以輸入多個文檔，然後默認輸出到 `/output` 度。佢默認輸入文件入面每一行都係一句話。運行下面嘅命令就得：

```bash
# 可以指定輸出路徑
python3 main.py --inputs input1.txt input2.txt --outdir output
# 亦可以剩係指定輸入，輸出會默認喺 /output
python3 main.py --inputs input.txt
```

## 原理

錯別字修正主要分兩種：規則錯別字同上下文錯別字。規則錯別字可以直接通過正則表達式替換嚟解決，例如`on9`永遠都可以直接替換成`戇鳩`，無需考慮上下文。上下文錯別字需要睇埋個詞嘅意義同語境先可以判斷得到佢個正字係乜。所有嘅規則錯別字都直接用正則表達式替換嚟修復，規則全部放喺 `regular.txt` 入面。上下文錯別字嘅修復規則都寫喺 `rules.py` 入面。每句輸入都會先修復規則錯別字，然後用 PyCantonese 分詞同標詞性，跟住`rules.py`先會根據每個詞詞性同上下文嚟修正錯別字。

## 致謝

[Zhanrui](https://github.com/ZhanruiLiang)

# Cantonese typo auto corrector

This is a Cantonese typo corrector, it auto corrects common Cantonese typos in the input texts.

The orthography of this corrector is from [粵文常見錯別字](https://jyutping.org/blog/typo/)

## Dependencies

- Python >= 3.9
- PyCantonese

## How to use

This typo corrector takes in one or more input text files, and outputs the corrected texts in the `output_dir`. It assumes each line in the input text file is one sentence.

To use the corrector, run the command:

```bash
# Specify the output dir
python3 main.py --inputs input1.txt input2.txt --outdir output
# Or put the input files only, output will be in /output by default
python3 main.py --inputs input.txt
```

## How it works

There are two types of typos: regular and contextual. Regular typos can be fixed by simple regex replacements. Contextual typos needs the pos tags and contextual information to fix. All regex rules for fixing regular typos are stored in `regular.txt`. Rules for fixing contextual typos are in `rules.py`.

## Credits

[Zhanrui](https://github.com/ZhanruiLiang)
