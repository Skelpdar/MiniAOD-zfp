import uproot

import lzma

from pyzfp import compress, decompress
import numpy as np

import sys

f = uproot.open("uncompressednanoaod.root")
ftrunc = uproot.open("nanoaod.root")

precisiondict = {}
with open("precision.txt") as precf:
    lines = [line.rstrip() for line in precf]
    for l in lines:
        precisiondict[l.split()[0]] = int(l.split()[1])

branches = f["Events"].keys()
branches = [str(k)[2:-1] for k in branches]

uncompressedsize = 0
compressedsize = 0
zfpcompressedsize = 0

zfpcompressedbranches = []

floatbranches = 0
totbranches = 0

float32 = str(f["Events/"+branches[25]].interpretation)

floatbranchnames = []

for kk in branches:
    branch = f["Events/"+kk]
    print(branch.name)
    totbranches += 1
    if str(branch.interpretation) == float32:
        print("Found 32 bit float")
        uncompressedsize += branch.uncompressedbytes()
        compressedsize += branch.compressedbytes()
        floatbranches += 1

        floatbranchnames.append(branch.name)

        n = precisiondict[str(branch.name)[2:-1]]

        tol = 2**(-n)

        flat = np.array([i for sublist in branch.array() for i in sublist])
        try:
            compressed = lzma.compress(bytes(compress(flat, tolerance=tol)))
            #decompressed = decompress(compressed, flat.shape, flat.dtype, tolerance=tol)
            #ratio = len(compressed)/len(flat.tostring())
            ratio = len(compressed)/len(bytes(flat))
            #ratio = (compressed.nbytes/flat.nbytes)
            print(n)
            print(ratio)
            zfpcompressedsize += ratio*branch.uncompressedbytes()
            zfpcompressedbranches.append(ratio*branch.uncompressedbytes())
        except:
            print("FAILED")
            zfpcompressedsize += branch.compressedbytes()
            zfpcompressedbranches.append(-1)
    else:
        print("Not float")
        uncompressedsize += branch.uncompressedbytes()
        compressedsize += branch.compressedbytes()
        zfpcompressedsize += branch.compressedbytes()
        zfpcompressedbranches.append(-1)

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
