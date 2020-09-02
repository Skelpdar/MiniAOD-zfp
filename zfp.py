from pyzfp import compress, decompress
import numpy as np
import matplotlib.pyplot as plt

import uproot

import lzma
import zlib
import lz4.frame
import zstd

f = uproot.open("nanoaod.root")
funcompressed = uproot.open("uncompressednanoaod.root")

branches = ["Jet_area"]

n = 4

X = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

ratio = [ 2**(-n) for n in X ]

percentageofsucessfulbranches = []

Y = []
Yzfpandlzma = []
Yzfpandzstd = []
Ylzma = []
Ylzmadefault = []
Yzlib = []
Ylz4 = []
Yzstd = []

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
            jaggedu = funcompressed["Events/"+k].array()
            subarraylengths = [len(k) for k in jagged]
           
            flat = np.array([i for sublist in jagged for i in sublist])

            subarraylengthsu = [len(k) for k in jaggedu]
           
            flatu = np.array([i for sublist in jaggedu for i in sublist])

            lzmauncompressed = len(bytes(flat))
            lzmacompressed = len(lzma.compress(bytes(flat), preset=9))

            Ylzma.append(lzmauncompressed/lzmacompressed)
            
            lzmauncompressed = len(bytes(flat))
            lzmacompressed = len(lzma.compress(bytes(flat)))   
            
            Ylzmadefault.append(lzmauncompressed/lzmacompressed)
    
            zlibuncompressed = len(bytes(flat))
            zlibcompressed = len(zlib.compress(bytes(flat), level=9))
            Yzlib.append(zlibuncompressed/zlibcompressed)
        
            lz4uncompressed = len(bytes(flat))
            lz4compressed = len(lz4.frame.compress(bytes(flat), compression_level=16))
            Ylz4.append(lz4uncompressed/lz4compressed)

            zstduncompressed = len(bytes(flat))
            zstdcompressed = len(zstd.compress(bytes(flat),22))

            Yzstd.append(zstduncompressed/zstdcompressed)

            tol = r

            compressed = compress(flatu, tolerance=tol)

            compressedwithlzma = lzma.compress(bytes(compressed))
            Yzfpandlzma.append(len(bytes(flatu))/len(bytes(compressedwithlzma)))

            compressedwithzstd = zstd.compress(bytes(compressed))
            Yzfpandzstd.append(len(bytes(flatu))/len(bytes(compressedwithzstd)))

            length = len(flatu.tostring())
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

ax1.set_title("NanoAOD " + str(branches[0]) + " (pure Python implementation)")

ax1.set_xlabel("-log_2(precision) (for solid lines)")

ax1.set_ylabel("Compression ratio")

ax1.plot([6,23],[Y[n],Y[n]],'--', label="zfp w/ CMSSW precision")

ax1.plot(X,Y,label="zfp w/ varying precision")

ax1.plot(X,Ylzma,'--', label="LMF + LZMA (max comp. lvl)")

#ax1.plot(X,Ylzmadefault,'--', label="LZMA (python) default")

ax1.plot(X,Yzlib,'--', label="LMF + ZLIB (max comp. lvl)")

ax1.plot(X,Ylz4,'--', label="LMF + lz4 (max comp. lvl)")

ax1.plot(X,Yzstd,'--', label="LMF + Zstd (max comp. lvl)")

ax1.plot(X,Yzfpandlzma,label="zfp then LZMA (max comp. lvl)")

ax1.plot(X,Yzfpandzstd,label="zfp then Zstd (max comp. lvl)")

ax1.set_xticks([6,8,10,12,14,16,18,20,22])

plt.legend(loc="upper right", fontsize="small")

plt.savefig("compression_NANOaod_" + str(branches[0]),dpi=300, transparent=True)

print(Yzfpandlzma[n])
print(Ylzma[0])

plt.show()
