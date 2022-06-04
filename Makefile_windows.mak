#added by python script


HDBASE = K:\jff\AmigaHD
WHDBASE = $(HDBASE)\PROJETS\HDInstall\DONE
EXE = kick31340.A1000

all :  $(EXE)
ASMEXE = vasmm68k_mot -no-opt -nosym  -maxerrors=0 -I$(HDBASE)/amiga39_JFF_OS/include -I$(WHDBASE)\WHDLoad\Include -I$(WHDBASE)  -nosym -Fhunkexe
ASMBIN = vasmm68k_mot -no-opt -nosym -maxerrors=0 -I$(HDBASE)/amiga39_JFF_OS/include -nosym -Fbin
# we need to make sure that nothing is shifted
# so we create a 100% identical object
# we test it against original object file
# now if all is OK build the actual executable
$(EXE) : kick31340.A1000.s
	$(ASMBIN) -o $(EXE) kick31340.A1000.s
	fc $(EXE) kick11_A1000_ref.rom	
	$(ASMEXE) -DREAL_EXE -o kick11_A1000_hunk kick31340.A1000.s
#$(ASMEXE) -DWA -o $(EXE) object.s


