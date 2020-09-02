from pyzfp import compress, decompress
import numpy as np
import matplotlib.pyplot as plt

from timeit import default_timer as timer

import uproot

import lzma
import zlib
import lz4.frame
import zstd

f = uproot.open("nanoaod.root")
funcompressed = uproot.open("uncompressednanoaod.root")

branches = ["Jet_rawFactor"]

n = 6

X = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

ratio = [ 2**(-n) for n in X ]

percentageofsucessfulbranches = []

N = 50

Y = []
Yratio = []

Yzfpandlzma = []
Yzfpandlzmaratio = []

Yzfpandzstd = []
Ylzma = []
Ylzmadefault = []
Ylzmafast = []
Yzlib = []
Yzlibfast = []
Ylz4 = []
Ylz4fast = []
Yzstd = []
Yzstdlow = []
Yzstddefault = []

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

            '''
            lzmauncompressed = len(bytes(flat))
            start = timer()
            lzmacompressed = len(lzma.compress(bytes(flat), preset=9))
            end = timer()
            Ylzma.append(end-start)
            
            lzmauncompressed = len(bytes(flat))
            start = timer()
            lzmacompressed = len(lzma.compress(bytes(flat)))   
            end = timer()
            Ylzmadefault.append(end-start)
    
            zlibuncompressed = len(bytes(flat))
            zlibcompressed = len(zlib.compress(bytes(flat), level=0))
            Yzlib.append(zlibuncompressed/zlibcompressed)
        
            lz4uncompressed = len(bytes(flat))
            lz4compressed = len(lz4.frame.compress(bytes(flat), compression_level=16))
            Ylz4.append(lz4uncompressed/lz4compressed)

            zstduncompressed = len(bytes(flat))
            zstdcompressed = len(zstd.compress(bytes(flat),22))

            Yzstd.append(zstduncompressed/zstdcompressed)
            '''
            if r == ratio[0]:
                data = bytes(flat)

                start = timer()
                for _ in range(0,N):
                    lz4compressed = lz4.frame.compress(data, compression_level=16)
                end = timer()
                Ylz4.append((end-start)/N*1000)
                Ylz4.append(len(data)/len(lz4compressed))

                start = timer()
                for _ in range(0,N):
                    lz4compressed = lz4.frame.compress(data, compression_level=0)
                end = timer()
                Ylz4fast.append((end-start)/N*1000)
                Ylz4fast.append(len(data)/len(lz4compressed))

                start = timer()
                for _ in range(0,N):
                    zlibcompressed = zlib.compress(data, level=9)
                end = timer()
                Yzlib.append((end-start)/N*1000)
                Yzlib.append(len(data)/len(zlibcompressed))

                start = timer()
                for _ in range(0,N):
                    zlibcompressed = zlib.compress(data, level=1)
                end = timer()
                Yzlibfast.append((end-start)/N*1000)
                Yzlibfast.append(len(data)/len(zlibcompressed))
                
                start = timer()
                for _ in range(0,N):
                    zstdcompressed = zstd.compress(data,22)
                end = timer()
                Yzstd.append((end-start)/N*1000)
                Yzstd.append(len(data)/len(zstdcompressed))

                start = timer()
                for _ in range(0,N):
                    zstdcompressed = zstd.compress(data,-5)
                end = timer()
                Yzstdlow.append((end-start)/N*1000)
                Yzstdlow.append(len(data)/len(zstdcompressed))
                
                start = timer()
                for _ in range(0,N):
                    zstdcompressed = zstd.compress(data,0)
                end = timer()
                Yzstddefault.append((end-start)/N*1000)
                Yzstddefault.append(len(data)/len(zstdcompressed))
                
                start = timer()
                for _ in range(0,N):
                    lzmacompressed = lzma.compress(data, preset=9)
                end = timer()
                Ylzma.append((end-start)/N*1000)
                Ylzma.append(len(data)/len(lzmacompressed))
                
                start = timer()
                for _ in range(0,N):
                    lzmacompressed = lzma.compress(data)
                end = timer()
                Ylzmadefault.append((end-start)/N*1000)
                Ylzmadefault.append(len(data)/len(lzmacompressed))
                
                start = timer()
                for _ in range(0,N):
                    lzmacompressed = lzma.compress(data, preset=0)
                end = timer()
                Ylzmafast.append((end-start)/N*1000)
                Ylzmafast.append(len(data)/len(lzmacompressed))

            tol = r

            start = timer()
            for _ in range(0,N):
                compressed = compress(flatu, tolerance=tol)
            end = timer()

            Y.append((end-start)/N*1000)
            Yratio.append(len(bytes(flatu))/len(bytes(compressed)))

            start1 = timer()
            for _ in range(0,N):
                compressed = compress(flatu, tolerance=tol)
            end1 = timer()

            data = bytes(compressed)

            start2 = timer()
            for _ in range(0,N):
                compressedwithlzma = lzma.compress(data, preset=1)
            end2 = timer()

            Yzfpandlzma.append((end1-start1 + end2-start2)/N*1000)
            Yzfpandlzmaratio.append(len(bytes(flatu))/len(bytes(compressedwithlzma)))
            #Yzfpandlzma.append(len(bytes(flatu))/len(bytes(compressedwithlzma)))

            #compressedwithzstd = zstd.compress(bytes(compressed))
            #Yzfpandzstd.append(len(bytes(flatu))/len(bytes(compressedwithzstd)))

            #length = len(flatu.tostring())
            #compressedlength = len(compressed)

            compressions += 1

            #print("Length: " + str(length))
            #print("Compressed length: " + str(compressedlength))

            #if length >= compressedlength:
            #    print("Effective!")
            #    sucesses += 1
            #else:
            #    print("Not effective.")

            #totlength += length
            #totcomplength += compressedlength

        except:
            print("Exception (probably holds some weird values)")
   
    #Y.append(totlength/totcomplength)
    #percentageofsucessfulbranches.append(sucesses/compressions)

fig, ax1 = plt.subplots()

ax1.set_title("NanoAOD " + str(branches[0]) + " (pure Python implementation)")

ax1.set_xlabel("-log_2(precision) (for solid lines)")

ax1.set_ylabel("Compression time (ms)")

ax1.plot([6,23],[Y[n],Y[n]],'--', label="zfp w/ CMSSW tolerance", color="mediumpurple")

ax1.plot(X,Y,label="zfp w/ varying precision", color="mediumpurple")

#ax1.plot(X,Ylzma,'--', label="LMF + LZMA (max comp. lvl)")

#ax1.plot(X,Ylzmadefault,'--', label="LZMA (python) default")

ax1.plot([6,23],[Yzlib[0],Yzlib[0]],'--', label="ZLIB (after LMF, max comp. lvl)", color="firebrick")

ax1.plot([6,23],[Yzlibfast[0],Yzlibfast[0]],'-.', label="ZLIB (after LMF, fast)", color="firebrick")

ax1.plot([6,23],[Ylz4[0],Ylz4[0]],'--', label="lz4 (after LMF, max comp. lvl)", color="steelblue")

ax1.plot([6,23],[Ylz4fast[0],Ylz4fast[0]],'-.', label="lz4 (after LMF, fastest)", color="steelblue")

ax1.plot([6,23],[Ylzma[0],Ylzma[0]],'-', label="LZMA (after LMF, max comp. lvl)", color="forestgreen")

#ax1.plot([6,23],[Ylzmadefault[0],Ylzmadefault[0]],'--', label="LZMA (after LMF, default comp. lvl)")

ax1.plot([6,23],[Ylzmafast[0],Ylzmafast[0]],'--', label="LZMA (after LMF, fastest)", color="forestgreen")

ax1.plot(X,Yzfpandlzma,'-.',label="zfp then LZMA (fastest)", color="forestgreen")

ax1.plot([6,23],[Yzstd[0],Yzstd[0]],'--', label="Zstd (after LMF, max comp. lvl)", color="orange")

ax1.plot([6,23],[Yzstdlow[0],Yzstdlow[0]], '-.', label="Zstd (after LMF, fastest)", color="orange")

ax1.plot([6,23],[Yzstddefault[0],Yzstddefault[0]], ':', label="Zstd (after LMF, Python default)", color="orange")

#ax1.plot(X,Yzfpandzstd,label="zfp then Zstd (max comp. lvl)")

ax1.set_xticks([6,8,10,12,14,16,18,20,22])

ax1.set_yscale("log")

plt.legend(loc="upper right", fontsize="small", bbox_to_anchor=(1.5,1.0))


plt.savefig("timing_NANOaod_" + str(branches[0]),dpi=300, transparent=True, bbox_inches="tight")



#print(Yzfpandlzma[n])
#print(Ylzma[0])

plt.show()

plt.title("NanoAOD " + str(branches[0]) + " (pure Python implementation)")
plt.ylabel("Compression time (ms)")

plt.bar([0,1,2,3,4,5], [Y[n],Yzstdlow[0],Yzstddefault[0], Yzlibfast[0], Ylz4[0], Ylz4fast[0]], width=0.4, align='center', color=["mediumpurple", "orange", "orange", "firebrick", "steelblue", "steelblue"])

plt.xticks([0,1,2,3,4,5], ["zfp\n(CMSSW tol.)","Zstd\n(fastest)\nafter LMF","Zstd\n(Python default)\nafter LMF","Zlib\n(fastest)\nafter LMF", "lz4\n(max comp. lvl)\nafter LMF", "lz4\n(fastest)\nafter LMF"])


plt.savefig("timing_NANOaod_bars_" + str(branches[0]),dpi=300, transparent=True)

plt.show()

plt.title("NanoAOD " + str(branches[0]) + " (pure Python implementation)")
plt.xlabel("Compression time (ms)")

plt.ylabel("Compression ratio")

plt.plot(Y, Yratio, color="mediumpurple", label="zfp")
plt.plot(Y, Yratio,'.', color="mediumpurple")
plt.text(Y[0],Yratio[0], "tol=2^-6")
plt.text(Y[-1],Yratio[-1], "tol=2^-23")

plt.plot(Yzlib[0],Yzlib[1],'.', color="firebrick", label="ZLIB (max comp.)")
plt.plot(Yzlibfast[0], Yzlibfast[1], '*', color="firebrick", label="ZLIB (fastest)")

plt.plot(Ylz4[0],Ylz4[1],'.',color="steelblue", label="lz4 (max comp.)")
plt.plot(Ylz4fast[0],Ylz4fast[1],'*',color="steelblue", label="lz4 (fastest)")

plt.plot(Yzfpandlzma, Yzfpandlzmaratio, color="forestgreen", label="zfp + LZMA (fastest)")
plt.plot(Yzfpandlzma, Yzfpandlzmaratio,'.', color="forestgreen")
plt.text(Yzfpandlzma[0],Yzfpandlzmaratio[0], "tol=2^-6")
plt.text(Yzfpandlzma[-1],Yzfpandlzmaratio[-1], "tol=2^-23")
plt.plot(Ylzma[0], Ylzma[1],'.',color="forestgreen", label="LZMA (max comp.)") 
plt.plot(Ylzmafast[0], Ylzmafast[1],'*',color="forestgreen", label="LZMA (fastest)") 

plt.plot(Yzstddefault[0], Yzstddefault[1], '.', color="orange", label="Zstd (Python default)")
plt.plot(Yzstdlow[0],Yzstdlow[1], '*', color="orange", label="Zstd (fastest)")

plt.legend()

plt.legend(loc="upper right", fontsize="small", bbox_to_anchor=(1.4,1.0))

plt.savefig("timing_NANOaod_versus_" + str(branches[0]),dpi=300, transparent=True, bbox_inches="tight")

plt.show()


