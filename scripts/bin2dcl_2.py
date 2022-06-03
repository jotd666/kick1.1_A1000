import os,re,struct
with open("../kick11_A1000_ref.rom","rb") as f:
    contents = f.read()

#0x0fc0674,0x0fc0730

start = int("0ff06e6",16)
end = int("0ff0704",16)
while start < end:
    i = start - 0xfc0000
    data = struct.unpack_from(">H",contents,i)[0]
    if data in [0xFC,0xFD,0xFE,0xFF]:
        data = struct.unpack_from(">I",contents,i)[0]
        print("\tdc.l\tlb_{:x}\t;{:07x}".format(data,start))
        start += 2
    else:
        print("\tdc.w\t${:x}\t;{:07x}".format(data,start))
    start += 2