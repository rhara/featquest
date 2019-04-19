#!/usr/bin/env python

import sys, os

srcdir = sys.argv[1]

LIGAND_ATOMS = 90

out = open('bulkrun.sh', 'wt')
ls = sorted([name for name in os.listdir(srcdir) if len(name) == 4])
print('#!/bin/bash')
print()
print('trap "exit 1" 2 15')
print()
for name in ls:
    if os.path.exists('%s/%s/%s_ligand.sdf' % (srcdir, name, name)) and \
       os.path.exists('%s/%s/%s_pocket.pdb' % (srcdir, name, name)):
        print('%s OK' % name)
        print('python atomic_conv.py -l %s/%s/%s_ligand.sdf -p %s/%s/%s_pocket.pdb --padding %d -o %s_out.npz' % (srcdir, name, name, srcdir, name, name, LIGAND_ATOMS, name), file=out)
    else:
        print('%s SKIPPED' % name, file=sys.stderr)
