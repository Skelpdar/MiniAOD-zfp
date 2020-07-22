from pyzfp import compress, decompress
import numpy as np
import matplotlib.pyplot as plt


import uproot

import lzma
import zlib
import lz4.frame

f = uproot.open("nanoFDA8C137.root")

branches = ["Jet_chHEF"]

n = 0

X = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

ratio = [ 2**(-n) for n in X ]

percentageofsucessfulbranches = []

Y = []
Ylzma = []
Yzlib = []
Ylz4 = []

for r in ratio:
    print("Tolerance = " + str(r) + " of smallest value")

    compressions = 0
    sucesses = 0

    totlength = 0
    totcomplength = 0
    
    for k in branches:
        print(" ")
        print(k)

        try:
            jagged = f["Events/"+k].array()
            subarraylengths = [len(k) for k in jagged]
           
            flat = np.array([i for sublist in jagged for i in sublist])

            lzmauncompressed = len(bytes(flat))
            lzmacompressed = len(lzma.compress(bytes(flat)))

            Ylzma.append(lzmauncompressed/lzmacompressed)
    
            zlibuncompressed = len(bytes(flat))
            zlibcompressed = len(zlib.compress(bytes(flat)))
            Yzlib.append(zlibuncompressed/zlibcompressed)
        
            lz4uncompressed = len(bytes(flat))
            lz4compressed = len(lz4.frame.compress(bytes(flat), compression_level=16))
            Ylz4.append(lz4uncompressed/lz4compressed)

            tol = r

            compressed = compress(flat, tolerance=tol)

            length = len(flat.tostring())
            compressedlength = len(compressed)

            compressions += 1

            print("Length: " + str(length))
            print("Compressed length: " + str(compressedlength))

            if length >= compressedlength:
                print("Effective!")
                sucesses += 1
            else:
                print("Not effective.")

            totlength += length
            totcomplength += compressedlength

        except:
            print("Exception (probably holds some weird values)")
   
    Y.append(totlength/totcomplength)
    percentageofsucessfulbranches.append(sucesses/compressions)

fig, ax1 = plt.subplots()

ax1.set_title("NanoAOD " + str(branches[0]))

ax1.set_xlabel("n (tolerance = 2^(-n))")

ax1.set_ylabel("Compression ratio")


ax1.plot([6,23],[Y[n],Y[n]],'--', label="zfp with true precision")

ax1.plot(X,Y,label="zfp with varying precision")

ax1.plot(X,Ylzma,'--', label="LZMA")

ax1.plot(X,Yzlib,'--', label="ZLIB")

ax1.plot(X,Ylz4,'--', label="lz4 w/ max compression lvl")

plt.legend()

plt.savefig("compression_NANOaod_" + str(branches[0]),dpi=300)

plt.show()
