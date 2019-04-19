#!/usr/bin/env python

import sys, os, shlex
import multiprocessing as mp
import subprocess as sp

srcdir = sys.argv[1]

LIGAND_ATOMS = 90

def worker(name):
    lig_fname = '%s/%s/%s_ligand.sdf' % (srcdir, name, name)
    pro_fname = '%s/%s/%s_pocket.pdb' % (srcdir, name, name)
    if os.path.exists(lig_fname) and \
       os.path.exists(pro_fname):
        command = 'python atomic_conv.py -l %s -p %s --padding %d -o %s_out.npz' % (lig_fname, pro_fname, LIGAND_ATOMS, name)
        print(command)
        proc = sp.Popen(shlex.split(command), universal_newlines=True, stdout=sp.PIPE, stderr=sp.STDOUT)
        out = proc.stdout.read().rstrip()
        print(out)
        ret = True
    else:
        ret = False
    return name, ret

out = open('bulkrun.sh', 'wt')
ls = sorted([name for name in os.listdir(srcdir) if len(name) == 4 and name[0] in '0123456789'])
pool = mp.Pool(mp.cpu_count())
try:
    for name, ret in pool.imap_unordered(worker, ls):
        pass
except KeyboardInterrupt:
    sys.exit(1)
