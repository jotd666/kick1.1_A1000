import os,re,struct
with open("../kick11_A1000_ref.rom","rb") as f:
    contents = f.read()

#0x0fc0674,0x0fc0730
#0X0fc0458,0x0fc0474
for i in range(int("0fcb8a4",16),int("0fcb8e2",16),2):
    addr = i
    i -= 0xfc0000
    data = struct.unpack_from(">H",contents,i)[0]
    print("\tdc.w\t${:04x}\t;{:07x}".format(data,addr))