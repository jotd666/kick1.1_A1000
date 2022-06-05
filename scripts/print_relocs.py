import struct,collections,itertools

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

            if hunk_type_str == "reloc32":
                data = f.read(hunk_size+4)
                reloc_offsets = [struct.unpack_from(">I",data,i)[0] for i in range(4,len(data),4)]
                break
            else:
                data = f.read(hunk_size)
        with open(binary_file,"rb") as f:
            data = f.read()
            reloc_values = {struct.unpack_from(">I",data,i)[0] for i in reloc_offsets}

            possible_reloc_values_bcpl = collections.defaultdict(list)
            possible_reloc_values = collections.defaultdict(list)
            for offset in range(0,len(data)-4,2):
                value = struct.unpack_from(">I",data,offset)[0]
                if (0xFC0000 <= value < 0xFFFFF0) and (value & 0xFF):
                    possible_reloc_values[value].append(offset)
                else:
                    value *= 4
                    if (0xFF0000 < value < 0xFFF000) and (value & 0xFF):
                        possible_reloc_values_bcpl[value].append(offset)

            fake_relocs = {0xff0001,0xff0004,0xff0082,0xff00bf,0xff0006,0xff0014,0xff0008,0xff0018,0xff6f0e,
            0xff0040,0xff000e,0xff0019,0xff001f,0xff01ff,0xff007f,0xff0050,0xff0009,0xff0058,0xff6706,0xff720a,
            0xfffff4,0xfe3002,0xfd001f,0xfe2241,0xff3604,0xff508f,0xff5343,0xff6602,0xff6624,0xff6704,0xff7608,
                    0xfe001f,0xfc001f,0x0fc4e95,0xfc49ec,0xfe0007,0xfe001e,0xff2342,0xff2f02,0xff4878,0xff4e75,
            0xfc222a,0xfc286a,0xfc2f0a,0xfc2f39,0xfc3d6a,0xfc3d6e,0xfc41ea,0xfc41f9,0xfc42a9,0xfc486e,0xfc4e75,
            0xfe722a,0xff528b,
            0xfcb2a9,0xfccf88,0xfe0053,0xfe0008,0xff0348,0xff0349,0xfe00bf,0xfe226e,0xfe2640,0xff2243,0xff2341,
            0xfe70ea,0xff0c43,0xff0fff,0xff8483,0xffb280,0xffc8b0}
            missed_relocs = set(possible_reloc_values).difference(reloc_values)
            nb_missing = len(missed_relocs-fake_relocs)
            if nb_missing:
                for mo in sorted(missed_relocs-fake_relocs):
                    print("0x{:x} (offsets 0{})".format(mo,",".join("{:x}".format(x+0xFC0000) for x in possible_reloc_values[mo])))
            else:
                # could have missed offsets
                possible_reloc_filtered_values = {k:v for k,v in possible_reloc_values.items() if k not in fake_relocs}

                possible_reloc_offsets = set(itertools.chain.from_iterable(possible_reloc_filtered_values.values()))

                offset_diff = possible_reloc_offsets.difference(set(reloc_offsets))
                if offset_diff:
                    print("All reloc values found but some offsets are missing")
                    for o in sorted(offset_diff):
                        print("{:x}".format(o+0xFC0000))
                    nb_missing = 0  #len(offset_diff)

            print("Possible reloc offsets: {}, reloc_offsets: {}, missed_relocs: {}".format(len(possible_reloc_values),
            len(reloc_values),nb_missing))


            for mo in sorted(possible_reloc_values_bcpl):
                 print("0x{:x} BCPL 0x{:x} (offsets 0{})".format(mo,mo//4,",".join("{:x}".format(x+0xFC0000) for x in possible_reloc_values_bcpl[mo])))
                 if any(x < 0x30000 for x in possible_reloc_values_bcpl[mo]):
                    possible_reloc_values_bcpl.pop(mo)

            print("BCPL reloc offsets: {}".format(len(possible_reloc_values_bcpl)))

            if not nb_missing:
                rtb_data = [0xde,0xad,0xc0,0xde,0,0,0]  # wrong checksum
                previous = 0

                reloc_offsets= sorted(reloc_offsets)
                for offset in reloc_offsets:
                    delta = offset-previous
                    # encode
                    if delta < 0x100:
                        rtb_data.append(delta)
                    elif delta < 0x10000:
                        rtb_data.append(0)
                        if len(rtb_data)%2:
                            rtb_data.append(0)
                        rtb_data.append(delta>>8)
                        rtb_data.append(delta & 0xFF)
                    else:
                        #not happening
                        raise Exception("Distance too long {:x}, prev {:x}".format(offset,previous))

                    previous = offset
                # end: problem if offset is odd, we need to put a 0 longword
                if len(rtb_data)%2:
                    # check if previous reloc was byte or word
                    if rtb_data[-3]:
                        # it was byte, just insert 3 zeros
                        rtb_data[-1:-1] = [0]*3
                    else:
                        # it was word, we'll support it if needed
                        raise Exception("??? last reloc is word, unsupported")

                rtb_data.extend([0]*4)

                rtb_data.extend([0xff]*4)
                for offset in sorted(itertools.chain.from_iterable(possible_reloc_values_bcpl.values())):
                    rtb_data.extend(struct.pack(">I",offset))
                rtb_data.extend([0]*8)

                print("saving .RTB file, {} bytes".format(len(rtb_data)))
                with open(binary_file+".RTB","wb") as f:
                    f.write(bytearray(rtb_data))
                print("saving .RTB.TXT file")
                with open(binary_file+".RTB.TXT","w") as f:
                    for s in reloc_offsets:
                        f.write("\tdc.l\t${:x}\n".format(s))

decode(r"../kick11_A1000_hunk",r"../kick31340.A1000")

#decode(r"../kick11_A1000_hunk",r"../kick33192.rom")