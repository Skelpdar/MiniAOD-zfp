import uproot

import lzma
from pyzfp import compress, decompress

import numpy as np
import matplotlib.pyplot as plt

import sys
from timeit import default_timer as timer

f = uproot.open("uncompressednanoaod.root")
ftrunc = uproot.open("nanoaod.root")

precisiondict = {}
with open("precision.txt") as precf:
    lines = [line.rstrip() for line in precf]
    for l in lines:
        precisiondict[l.split()[0]] = int(l.split()[1])

branches = f["Events"].keys()
branches = [str(k)[2:-1] for k in branches]

#I.e. the x-axis, with the specified CMSSW mantissa bit length for every branch
tollist = []
#Compression speed for zfp + LZMA
zfpspeed = []
#Compression ratio -||-
zfpratio = []
#for LZMA (after LMF)
lzmaspeed = []
#for LZMA (after LMF)
lzmaratio = []

#string representation of our jagged float arrays
float32 = "asjagged(asdtype('>f4'))"

#Iterate through all branches and compress the float ones
for kk in branches:
    branch = f["Events/"+kk]
    branchtrunc = f["Events/"+kk]
    print(branch.name)
    if str(branch.interpretation) == float32:
        print("Found 32 bit float")

        n = precisiondict[str(branch.name)[2:-1]]

        tol = 2**(-n)

        flat = np.array([i for sublist in branch.array() for i in sublist])
        flattrunc = np.array([i for sublist in branchtrunc.array() for i in sublist])

        #Some branches are empty etc. and may fail. Not very important that they are missed
        try:
            start1 = timer()
            compressed = compress(flat, tolerance=tol)
            end1 = timer()
            zfpcompressed = bytes(compressed)
            start2 = timer()
            compressed = lzma.compress(zfpcompressed,preset=9)
            end2 = timer()

            flatsize = len(bytes(flat))
            compsize = len(compressed)

            zfpspeed.append(flatsize/(end1-start1+end2-start2)/1000000)
            zfpratio.append(flatsize/compsize)

            start = timer()
            compressed = lzma.compress(bytes(flattrunc), preset=9)
            end = timer()

            flatsize = len(bytes(flattrunc))
            compsize = len(compressed)

            lzmaspeed.append(flatsize/(end-start)/1000000)
            lzmaratio.append(flatsize/compsize)

            tollist.append(n)

        except Exception as e:
            print(e)
    else:
        print("Not float")

plt.title("Lossy compression of branches with CMSSW precisions")

plt.xlabel("Tolerance (mantissa bits)")
plt.ylabel("Compression ratio")

plt.plot(tollist, zfpratio, 'o', label="zfp + LZMA (max comp.)", color="mediumpurple")
plt.plot(tollist, lzmaratio, '.', label="LZMA (after LMF, max comp.)", color="forestgreen")

plt.legend()

plt.ylim([0,15])
plt.xlim([4,24])

plt.xticks([6,8,10,12,14,23])

plt.savefig("tolvsratio.png", dpi=300)

plt.show()

plt.title("Lossy compression of branches with CMSSW precisions")

plt.xlabel("Tolerance (mantissa bits)")
plt.ylabel("Compression speed (MB/S)")

plt.plot(tollist, zfpspeed, 'o', label="zfp + LZMA (max comp.)", color="mediumpurple")
plt.plot(tollist, lzmaspeed, '.', label="LZMA (after LMF, max comp.)", color="forestgreen")

plt.legend()

plt.xticks([6,8,10,12,14,23])

plt.xlim([4,24])

plt.savefig("tolvsspeed.png", dpi=300)

plt.show()
