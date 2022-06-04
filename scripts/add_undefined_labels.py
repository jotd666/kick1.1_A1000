import ira_asm_tools,subprocess,re,os

asmname = "../kick31340.A1000.s"
ud = re.compile("undefined symbol <lb_(\w+)>")
build = "vasmm68k_mot -I.. -no-opt -nosym -maxerrors=0 -nosym -Fbin -o wtf".split()+[asmname]
build = "cmd /c make -f Makefile_windows.mak".split()
p = subprocess.run(build,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,cwd="..")
if p.returncode:
    undefs = set()
    for line in p.stderr.splitlines():
        print(line)
        m = ud.search(line.decode())
        if m:
            undefs.add(int(m.group(1),16))

    af = ira_asm_tools.AsmFile(asmname)

    for u in undefs:
        offset = 0
        lineno = af.address_lines.get(u)
        if lineno is None:
            offset = 2
            lineno = af.address_lines.get(u-2)

        if lineno is None or offset:
            print("not done",lineno,hex(u),offset)
        else:
            print(lineno,hex(u),offset)
            af.lines[lineno] = "lb_{:05x}:\n{}".format(u,af.lines[lineno])
    with open(asmname,"w") as f:
        f.writelines(af.lines)