#!/usr/bin/env python

"""
Atomic Conv for Complex inspired by Pande
"""
import sys, argparse, time
from rdkit import Chem
import numpy as np


__VERSION__ = '0.1.0'
__AUTHOR__ = 'hara.ryuichiro@gmail.com'

np.set_printoptions(precision=3, suppress=True, threshold=np.inf, linewidth=300)


class Timer:
    def __init__(self, dt=10.0):
        self.dt = dt
        self.T0 = time.time()
        self.T = self.T0

    def check(self):
        ret = False
        t = time.time()
        if self.dt < t - self.T:
            self.T += self.dt
            ret = True
        return ret

    def elapsed(self):
        return time.time() - self.T0


class ComplexFeaturizer:

    def __init__(self,
                 atomtype_list=[6,7,8,9,11,12,15,16,17,20,25,30,35,53],
                 nneighbors=12,
                 radials=(1.5,12.,.5),
                 r0=1.5,
                 sigma0=1,
                 beta0=1.,
                 bias0=0.,
                 padding=70):

        self.atomtype_list = atomtype_list
        self.nneighbors = nneighbors
        self.radials = np.arange(radials[0], radials[1]+1e-7, radials[2])
        self.r0 = r0
        self.sigma0 = sigma0
        self.beta0 = beta0
        self.bias0 = bias0
        self.padding = padding

    def getNeighbors(self, lig, pro):
        """
        Make R (distance) and Z (atomtype) of neighboring atoms
        Note: neighbor size is defined as self.M
        """
        types_lig = np.array(list(map(lambda a: a.GetAtomicNum(), lig.GetAtoms())))
        types_pro = np.array(list(map(lambda a: a.GetAtomicNum(), pro.GetAtoms())))

        N_lig = lig.GetNumAtoms()
        N_pro = pro.GetNumAtoms()

        coords_lig = lig.GetConformer(0).GetPositions()
        coords_pro = pro.GetConformer(0).GetPositions()

        neighbors = np.zeros((N_lig, self.nneighbors), dtype=np.int)
        R = np.zeros((N_lig, self.nneighbors))
        Z = np.zeros((N_lig, self.nneighbors), dtype=np.int)

        for i in range(N_lig):
            mcoords = np.tile(coords_lig[i], N_pro).reshape((N_pro, 3))
            dist_vec = np.linalg.norm(mcoords - coords_pro, axis=1)
            neighbors[i] = np.argsort(dist_vec)[:self.nneighbors]
            R[i] = dist_vec[neighbors[i]]
            Z[i] = types_pro[neighbors[i]]

        return R, Z

    def atomTypeConvolution(self, R, Z):
        """
        Do the atom type convolution
        R(N,M), Z(N,M) -> E(N,M,Nat)
        """

        Na = len(self.atomtype_list)
        stacks = []
        for k in range(Na):
            atomtype = self.atomtype_list[k]
            Ka = (Z == atomtype).astype(np.int)
            v = R*Ka
            stacks.append(v)
        E = np.dstack(stacks)

        return E

    def radialPooling(self, E):
        """
        Do the radialPooling
        E(N,M,Nat) -> P(N,Nat,Nr)
        """

        def fc(r, cutoff):
            return (r < cutoff)*(np.cos(np.pi*r/cutoff) + 1)

        def fs(r, cutoff):
            return np.exp(-(r-r0)*(r-r0)*fc(r, cutoff)/sigma0/sigma0)

        r0 = self.r0
        sigma0 = self.sigma0
        beta = np.ones_like(self.radials)*self.beta0
        bias = np.ones_like(self.radials)*self.bias0

        N = E.shape[0]
        Na = len(self.atomtype_list)
        Nr = len(self.radials)

        P = np.zeros([N, Na, Nr])
        v0 = self.beta0*np.sum(fs(np.zeros(Na), self.radials[-1])) + self.bias0
        for i in range(Nr):
            cutoff = self.radials[i]
            for j in range(N):
                for k in range(Na):
                    r_list = E[j,:,k]
                    if np.all(r_list == 0.):
                        P[j, k, i] = v0
                    else:
                        P[j, k, i] = beta[i]*np.sum(fs(r_list, cutoff)) + bias[i]
        if N < self.padding:
            _P = np.ones([self.padding - N, Na, Nr])*v0
            P = np.vstack((P, _P))
        return P

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert pair of bound-complex molecules into '
                                                 'Pande-type atomic conv pooling layer')
    parser.add_argument('--ligand', '-l', type=str, required=True, dest='iname_lig', help='Ligand file')
    parser.add_argument('--protein', '-p', type=str, required=True, dest='iname_pro', help='Potein file')
    parser.add_argument('--neighbor-size', '-M', type=int, default=12, dest='nneighbors', help='Neighbor size')
    parser.add_argument('--radials', '-R', type=str, default='1.5 12.0 0.5', help='Radials setup')
    parser.add_argument('--r0', type=float, default=1.5, help='r_s')
    parser.add_argument('--sigma0', type=float, default=1., help='sigma_s')
    parser.add_argument('--beta0', type=float, default=1., help='Pre-learn uniformed value for beta')
    parser.add_argument('--bias0', type=float, default=-0.155525951535392, help='Pre-learn uniformed value for bias')
    parser.add_argument('--output', '-o', type=str, default='out.npz', dest='oname', help='Output file')
    parser.add_argument('--padding', type=int, default=70, help='Padding size')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose print')
    args = parser.parse_args()

    for lig in Chem.SDMolSupplier(args.iname_lig, sanitize=False): break
    if not lig:
        print('Error reading "%s" and skipped' % args.iname_lig)
        sys.exit(-1)

    pro = Chem.MolFromPDBFile(args.iname_pro)
    if not pro:
        print('Error reading "%s" and skipped' % args.iname_pro)
        sys.exit(-1)

    print('natoms: %s = %d, %s = %d' % (args.iname_lig, lig.GetNumAtoms(), args.iname_pro, pro.GetNumAtoms()))

    if args.padding < lig.GetNumAtoms():
        print('Error: Ligand "%s" is too big and is skipped' % args.iname_lig)
        sys.exit(-1)

    if 8000 < pro.GetNumAtoms():
        print('Error: Protein "%s" is too big and is skipped' % args.iname_pro)
        sys.exit(-1)

    featurizer = ComplexFeaturizer(nneighbors=args.nneighbors,
                                   radials=(1.5,12.,.5),
                                   r0=args.r0,
                                   sigma0=args.sigma0,
                                   beta0=args.beta0,
                                   bias0=args.bias0,
                                   padding=args.padding)

    R, Z = featurizer.getNeighbors(lig, pro)
    E = featurizer.atomTypeConvolution(R, Z)
    P = featurizer.radialPooling(E)

    np.savez(args.oname, iname_lig=args.iname_lig, iname_pro=args.iname_pro, R=R, Z=Z, E=E, P=P)
    if args.verbose:
        print('-------------------- R --------------------')
        print(R)
        print('-------------------- Z --------------------')
        print(Z)
        print('-------------------- E --------------------')
        print(E)
        print('-------------------- P --------------------')
        print(P)
        print(P.shape)
