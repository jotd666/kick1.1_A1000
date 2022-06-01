import struct,collections

hunk_dict = {0x3F3:"header",0x3E9:"code",0x3EA:"data",0x3F2:"end",0x3EC:"reloc32",0x3EB:"bss",0x3F1:"debug"}
def read_long(f):

    return struct.unpack(">I",f.read(4))[0]

def decode(input_file,binary_file):
    with open(input_file,"rb") as f:

        header = read_long(f)
        if header != 0x3F3:
            raise Exception("wrong header")
        strings = read_long(f)
        nb_hunks = read_long(f)
        start_hunk = read_long(f)
        end_hunk = read_long(f)
        hunk_sizes = []
        for _ in range(nb_hunks):
            value = read_long(f)
            # flags, value
            hunk_sizes.append(((value & 0xC0000000) >> 29,value & 0x3FFFFFFF))

        print("nb_hunks = {}, start = {}, end = {}".format(nb_hunks,start_hunk,end_hunk))

        i = 1
        while(True):
            # now the hunks (no need to remind the memory constraints)
            hunk_type = (read_long(f) & 0x3FFFFFFF)
            if hunk_type == 0x3F2:
                continue
            hunk_size = read_long(f)*4  # should be the same as the one previously read
            if not hunk_size:
                break
            hunk_type_str = hunk_dict.get(hunk_type,str(hunk_type))
            print("Hunk #{}, offset ${:06x} type ${:04x} ({}), size ${:x}".format(i,f.tell()-8,hunk_type,hunk_type_str,hunk_size))
            i+=1
            data = f.read(hunk_size)
            if hunk_type_str == "reloc32":
                reloc_offsets = [struct.unpack_from(">I",data,i)[0] for i in range(4,len(data),4)]

        with open(binary_file,"rb") as f:
            data = f.read()
            reloc_values = {struct.unpack_from(">I",data,i)[0] for i in reloc_offsets}

            possible_reloc_values = collections.defaultdict(list)
            for offset in range(0,len(data)-4,2):
                value = struct.unpack_from(">I",data,offset)[0]
                if (0xFC0000 < value < 0xFF0000) and (value & 0xFF):
                    possible_reloc_values[value].append(offset)
            fake_relocs = {0xfffff4,0xfe3002}
            missed_relocs = set(possible_reloc_values).difference(reloc_values)
            for mo in sorted(missed_relocs-fake_relocs):
                print("{:x} (offsets {})".format(mo,",".join("{:x}".format(x+0xFC0000) for x in possible_reloc_values[mo])))
            print("Possible reloc offsets: {}, reloc_offsets: {}, missed_relocs: {}".format(len(possible_reloc_values),
            len(reloc_values),len(missed_relocs)))

decode(r"../kick11_A1000_hunk",r"../kick11_A1000.rom")

