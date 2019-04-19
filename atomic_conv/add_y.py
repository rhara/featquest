import numpy as np
import sys

dname = sys.argv[1]
indexname = sys.argv[2]
oname = sys.argv[3]

value_map = {}
for line in open(indexname, 'rt'):
    if line.startswith('#'):
        continue
    it = line.rstrip().split(maxsplit=5)
    code = it[0]
    val = float(it[3])
    value_map[code] = val

d = np.load(dname)
y = np.zeros(len(d['codes']))
for i, code in enumerate(d['codes']):
    try:
        v = value_map[code]
        print(code, v)
    except:
        v = np.nan
        print(code, v)
    y[i] = v

np.savez(oname, X=d['X'], codes=d['codes'], y=y)
