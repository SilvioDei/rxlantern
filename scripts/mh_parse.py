import re, html, sys
from pathlib import Path
TAG = re.compile(r'</?[a-zA-Z][^>]*>')
def clean(s):
    s = re.sub(r'<span style="display:none;">.*?</span>', '', s, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(TAG.sub('', s))).strip()
def rows(path):
    t = Path(path).read_text(encoding="utf-8")
    m = re.search(r'<table class="ma__table"[^>]*id="drug">(.*?)</table>', t, re.S)
    if not m: return []
    return [[clean(x) for x in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
            for tr in re.findall(r'<tr class="(?:odd|even)">(.*?)</tr>', m.group(1), re.S)]
if __name__ == "__main__":
    for f in sys.argv[1:]:
        print("==", Path(f).stem)
        for r in rows(f): print("   ", " | ".join(r))
