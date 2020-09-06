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

#uncompressedsize = 0
#compressedsize = 0
#zfpcompressedsize = 0

#zfpcompressedbranches = []

#floatbranches = 0
#totbranches = 0

zfpspeed = []
zfpratio = []
lzmaspeed = []
lzmaratio = []

float32 = str(f["Events/"+branches[25]].interpretation)

#floatbranchnames = []

for kk in branches[:100]:
    branch = f["Events/"+kk]
    branchtrunc = f["Events/"+kk]
    print(branch.name)
    #totbrancddhes += 1
    if str(branch.interpretation) == float32:
        print("Found 32 bit float")
        #uncompressedsize += branch.uncompressedbytes()
        #compressedsize += branch.compressedbytes()
        #floatbranches += 1

        #floatbranchnames.append(branch.name)

        n = precisiondict[str(branch.name)[2:-1]]

        tol = 2**(-n)

        flat = np.array([i for sublist in branch.array() for i in sublist])
        flattrunc = np.array([i for sublist in branchtrunc.array() for i in sublist])
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

            #decompressed = decompress(compressed, flat.shape, flat.dtype, tolerance=tol)
            #ratio = len(compressed)/len(flat.tostring())
            #ratio = len(compressed)/len(bytes(flat))
            #ratio = (compressed.nbytes/flat.nbytes)
            #print(n)
            #print(ratio)
            #zfpcompressedsize += ratio*branch.uncompressedbytes()
            #zfpcompressedbranches.append(ratio*branch.uncompressedbytes())
        except Exception as e:
            print(e)
            #zfpcompressedsize += branch.compressedbytes()
            #zfpcompressedbranches.append(-1)
    else:
        print("Not float")
        #uncompressedsize += branch.uncompressedbytes()
        #compressedsize += branch.compressedbytes()
        #zfpcompressedsize += branch.compressedbytes()
        #zfpcompressedbranches.append(-1)

plt.title("Lossy compression of branches with CMSSW precisions")

plt.xlabel("Compression speed (MB/s)")
plt.ylabel("Compression ratio")

plt.plot(zfpspeed, zfpratio, '.', label="zfp + LZMA (max comp.)", color="mediumpurple")
plt.plot(lzmaspeed, lzmaratio, '.', label="LMF + LZMA (max comp.)", color="forestgreen")

plt.legend()

plt.ylim([0,10])
plt.xlim([0,15])

plt.show()

'''
print("Percentage of branches that are floats: " + str(floatbranches/totbranches))

print("Uncompressed size: " + str(uncompressedsize))
print("Compressed size:   " + str(compressedsize))
print("zfp comprresed size (LZMA for non zfp branches): " + str(zfpcompressedsize))

truncatedcompressedsize = 0

lzmacompressedbranches = []

for kk in branches:
    branch = ftrunc["Events/"+kk]
    truncatedcompressedsize += branch.compressedbytes()
    lzmacompressedbranches.append(branch.compressedbytes())

print("Size for float truncated LZMA: " + str(truncatedcompressedsize))    

effective = 0
tot = 0

for kk in range(0,len(zfpcompressedbranches)):
    if zfpcompressedbranches[kk] != -1:
        tot += 1
        if zfpcompressedbranches[kk] < lzmacompressedbranches[kk]:
            effective += 1

print(effective/tot)
'''

