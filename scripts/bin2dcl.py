import os,re,struct
with open("../kick11_A1000_ref.rom","rb") as f:
    contents = f.read()

#0x0fc0674,0x0fc0730
#0X0fc0458,0x0fc0474
for i in range(int("0ff073c",16),int("0ff0758",16),4):
    addr = i
    i -= 0xfc0000
    data = struct.unpack_from(">I",contents,i)[0]
    if data:
        print("\tdc.l\tlb_{:x}\t;{:07x}".format(data,addr))
    else:
        print("\tdc.l\t${:x}\t;{:07x}".format(data,addr))
