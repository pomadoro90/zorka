import re, glob, os, json, sys
from datetime import datetime, timedelta
TR = str.maketrans({'S':'5','s':'5','O':'0','o':'0','Q':'0','D':'0','A':'4','l':'1','I':'1','i':'1','|':'1','!':'1','T':'7','Z':'2','z':'2','B':'8','G':'6','g':'9','q':'9','€':'6','b':'6',',':'.','?':'7'})
DATE = re.compile(r'(\d)\s?(\d)\s*[.,]\s*(\d)\s?(\d)\s*[.,]\s*(\d)\s?(\d)\s*(\d)\s?(\d)\s*[:.;\-]+\s*0\s?0')
def parse_vals(rest):
    rest = rest.translate(TR)
    rest = re.sub(r'(\d)\.\s+(\d\d)\b', r'\1.\2', rest)       # "3445. 56"
    rest = re.sub(r'\b(\d)\s+(\d\d)\b(?=\s+\d+\s*$)', r'\1.\2', rest)  # temp missing dot "4 64 120"
    toks = re.findall(r'[0-9.#x]+', rest)
    toks = [t.strip('.') for t in toks if t.strip('.')]
    out = []
    for t in toks:
        m = re.fullmatch(r'(\d+?)(\d{4}\.\d\d)', t)
        if m and len(m.group(1)) >= 1 and len(out) == 2:   # flow merged with pressure
            out += [m.group(1), m.group(2)]
        else:
            out.append(t)
    return out
def parse_file(path):
    rows = []
    for ln, line in enumerate(open(path).read().splitlines()):
        if not line.strip(): continue
        L = line.translate(TR)
        m = DATE.search(L[:30])
        if m:
            d = m.groups()
            date = (int(d[0]+d[1]), int(d[2]+d[3]), int(d[4]+d[5]), int(d[6]+d[7]))
            vals = parse_vals(line[m.end():] if len(line)==len(L) else L[m.end():])
            rows.append({'kind':'row','date':date,'vals':vals,'raw':line})
        elif re.search(r'(?i)(итого|uroro|utoro|roro|toro|wroro|viroro|итог)', line) or re.fullmatch(r'\s*\S{0,6}\s+0\s*', line):
            vals = parse_vals(re.sub(r'^\s*\S+', '', line))
            rows.append({'kind':'itogo','vals':vals,'raw':line})
        else:
            vals = parse_vals(re.sub(r'^[^0-9]*', '', line))
            rows.append({'kind':'other','vals':vals,'raw':line})
    return rows
if __name__ == '__main__':
    for r in parse_file(sys.argv[1]): print(r['kind'], r.get('date'), r['vals'])
