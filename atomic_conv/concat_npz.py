#!/usr/bin/env python

import sys, os, re
import numpy as np

np.set_printoptions(precision=3, suppress=True, threshold=np.inf, linewidth=300)

pat = re.compile('/(....)/')
dall = []
codes = []
count = 0
for name in os.listdir('.'):
    if name.endswith('_out.npz'):
        d = np.load(name)
        iname_pro = d['iname_pro'].item()
        m = pat.search(iname_pro)
        if m:
            code = m.group(1)
            codes.append(code)
        else:
            continue
        count += 1
        print(count, name)
        P = d['P']
        dall.append(P)
dall = np.array(dall)
print(dall.shape)
np.savez('all.npz', X=dall, codes=codes)
