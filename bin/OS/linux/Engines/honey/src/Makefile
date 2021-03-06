
### ==========================================================================
### Copyright Notice and License Information
### ==========================================================================
###   Honey, a UCI chess playing engine derived from SugaR, Stockfish and Glaurung 2.1
###   Copyright (C) 2004-2008 Tord Romstad (Glaurung Author)
###   Copyright (C) 2008-2015 Marco Costalba, Joona Kiiski, Tord Romstad (Stockfish Authors)
###   Copyright (C) 2015-2016 Marco Costalba, Joona Kiiski, Gary Linscott, Tord Romstad (Stockfish Authors)
###   Copyright (C) 2017-2018 Michael Byrne, Marco Zerbinati, Marco Costalba, Joona Kiiski, Gary Linscott, Tord Romstad (Honey Authors)

###   Honey is free software: you can redistri/Volumes/Macintosh_1.5TBbute it and/or modify
###   it under the terms of the GNU General Public License as published by
###   the Free Software Foundation, either version 3 of the License, or
###   (at your option) any later version.

###   Honey is distributed in the hope that it will be useful,
###   but WITHOUT ANY WARRANTY; without even the implied warranty of
###   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
###   GNU General Public License for more details.

###   You should have received a copy of the GNU General Public License
###   along with this program.  If not, see <http://www.gnu.org/licenses/>.
### ==========================================================================
### Section 1. General Configuration
### ==========================================================================

DATE=$(shell date +"%m%d%y")
DATE2=$(shell date +"%m%d")

### Fortress Detection code that will help in positions such as this:
### 3r4/3r4/2p1k3/p1pbPp1p/Pp1p1PpP/1P1P2R1/2P4R/2K1Q3 w - - 0 6, bm Rxg4
### Fortress Detection code by Joe Ellis:
### https://github.com/jhellis3/Stockfish/tree/game_cycle
###	FORT = yes

### HONEY=yes

### Diamond evaluation based on Crystal by Joe Ellis
### https://github.com/jhellis3/Stockfish/tree/crystal
###	NOIR = yes

### Bluefish evaluation by Eelco de Groot
### http://talkchess.com/forum3/viewtopic.php?f=2&t=71929
###	BLAU = yes

### Weakfish has about 90% of the search code Elo improvements removed
### WEAK = yes

### Release versions , enter yes and release version below foor releases
RELEASEVER = yes
RELVERSION = XI-r3

### TEST versions, enter yes and labels below to build named test exe's
TEST = no
TESTv1 = $(DATE2)
TESTv2 = NO_PROF
ifeq ($(TEST),yes)
	CXXFLAGS += -DTest
endif

### Uncomment for use with Raspberry Pi -  a slower NPS UCI option setting used in Play
### by Elo and personalities
###	RASPBERRY=Pi

### Features include : Cerebellum book functionality, play by Elo (UCI limit strength), keyboard shortcuts and a few other items. Comment out to eliminate
	FEATURE1=yes

### should be no reason to change anything below here!
### Only Honey with feature 1 will be publicly distributed at this time

ifeq ($(FEATURE1),yes)
	CXXFLAGS += -DAdd_Features
	FILES = with_c_book
	SUF =
endif

###  to reduce NPS setting using "setoption" command, to enable more similiar play when
###  playimg at reduced strength on hardware
ifeq ($(RASPBERRY),Pi)
	CXXFLAGS += -DPi
endif
ifeq ($(HONEY),yes)
    NAME=$(PRE)Honey$(SUF)
    CXXFLAGS += -DSullivan
	ifeq ($(BLAU),yes)
		CXXFLAGS += -DBlau
		PRE=Blue-
	endif
	ifeq ($(RELEASEVER),no)
		ifeq ($(TEST),no)
			ifeq ($(COMP),mingw)
				EXE = $(NAME)-dev-$(DATE).exe
			else
				EXE = $(NAME)-dev-$(DATE)
			endif
		endif
		ifeq ($(TEST),yes)
		        ifeq ($(COMP),mingw)
			        EXE = $(NAME)-$(TESTv1)-$(TESTv2).exe
		        else
			        EXE = $(NAME)-$(TESTv1)-$(TESTv2)
                        endif
		endif
	endif
	ifeq ($(RELEASEVER),yes)
        CXXFLAGS += -DReleaseVer
		ifeq ($(COMP),mingw)
			EXE = $(NAME)-$(RELVERSION).exe
		else
			EXE = $(NAME)-$(RELVERSION)
		endif
	endif
endif

### Note:  For building cur-dev stockfish with the features added.
ifeq ($(NOIR),yes)
	CXXFLAGS += -DNoir
	NAME=Black-Diamond
endif
ifneq ($(HONEY),yes)
	ifneq ($(NOIR),yes)
		ifeq ($(BLAU),yes)
			CXXFLAGS += -DBlau
			PRE=Blue
		else ifeq ($(WEAK),yes)
			CXXFLAGS += -DWeakfish
			PRE=Weak
		else
			PRE=Stock
			STOCKFISH = yes
			CXXFLAGS += -DStockfish
		endif
	NAME=$(PRE)fish$(SUF)
endif
	ifeq ($(RELEASEVER),no)
                ifeq ($(TEST),no)
		  ifeq ($(COMP),mingw)
			  EXE = $(NAME)-dev-$(DATE).exe
		  else
			  EXE = $(NAME)-dev-$(DATE)
    		  endif
                endif
		ifeq ($(TEST),yes)
		  ifeq ($(COMP),mingw)
			  EXE = $(NAME)-$(TESTv1)-$(TESTv2).exe
                  else
			  EXE = $(NAME)-$(TESTv1)-$(TESTv2)
                  endif
                endif
	endif
	ifeq ($(RELEASEVER),yes)
		CXXFLAGS += -DReleaseVer
		ifeq ($(COMP),mingw)
			EXE = $(NAME)-$(RELVERSION).exe
		else
		EXE = $(NAME)-$(RELVERSION)
		endif
	endif
endif

### Installation dir definitions
PREFIX = /opt/local
#PREFIX = /usr/local
BINDIR = $(PREFIX)/bin

### Built-in benchmark for pgo-builds
ifeq  ($(WEAK),yes)
PGOBENCH  = ./$(EXE) bench 16 1 8
endif
ifeq  ($(NOIR),yes)
PGOBENCH  = ./$(EXE) bench 16 1 12
PGOBENCH2 = ./$(EXE) bench 16 2 5
endif
ifeq  ($(STOCKFISH),yes)
PGOBENCH  = ./$(EXE) bench 16 1 18
PGOBENCH2 = ./$(EXE) bench 16 2 7
endif
ifeq  ($(HONEY),yes)
PGOBENCH  = ./$(EXE) bench 16 1 18
PGOBENCH2 = ./$(EXE) bench 16 2 10
endif
ifeq  ($(BLAU),yes)
PGOBENCH  = ./$(EXE) bench 16 1 18
PGOBENCH2 = ./$(EXE) bench 16 2 10
endif

### Object files
ifeq ($(FILES),with_c_book)
	OBJS = benchmark.o bitbase.o bitboard.o endgame.o evaluate.o main.o \
	material.o misc.o movegen.o movepick.o pawns.o position.o psqt.o \
	search.o thread.o timeman.o tt.o uci.o ucioption.o polybook.o tune.o syzygy/tbprobe.o
else
	OBJS = benchmark.o bitbase.o bitboard.o endgame.o evaluate.o main.o \
		material.o misc.o movegen.o movepick.o pawns.o position.o psqt.o \
		search.o thread.o timeman.o tt.o uci.o ucioption.o tune.o syzygy/tbprobe.o
endif

### Establish the operating system name
KERNEL = $(shell uname -s)
ifeq ($(KERNEL),Linux)
	OS = $(shell uname -o)
endif

### ==========================================================================
### Section 2. High-level Configuration
### ==========================================================================
#
# flag                --- Comp switch      --- Description
# ----------------------------------------------------------------------------
#
# debug = yes/no      --- -DNDEBUG         --- Enable/Disable debug mode
# sanitize = undefined/thread/no (-fsanitize )
#                     --- ( undefined )    --- enable undefined behavior checks
#                     --- ( thread    )    --- enable threading error  checks
# optimize = yes/no   --- (-O3/-fast etc.) --- Enable/Disable optimizations
# arch = (name)       --- (-arch)          --- Target architecture
# bits = 64/32        --- -DIS_64BIT       --- 64-/32-bit operating system
# prefetch = yes/no   --- -DUSE_PREFETCH   --- Use prefetch asm-instruction
# popcnt = yes/no     --- -DUSE_POPCNT     --- Use popcnt asm-instruction
# sse = yes/no        --- -msse            --- Use Intel Streaming SIMD Extensions
# pext = yes/no       --- -DUSE_PEXT       --- Use pext x86_64 asm-instruction
#
# Note that Makefile is space sensitive, so when adding new architectures
# or modifying existing flags, you have to make sure there are no extra spaces
# at the end of the line for flag values.

### 2.1. General and architecture defaults
optimize = yes
debug = no
sanitize = no
bits = 64
prefetch = no
popcnt = no
sse = no
pext = no
native = no

threadripper = no
### 2.2 Architecture specific

### native
ifeq ($(native),yes)
CXXFLAGS += -march=native
endif

ifeq ($(ARCH),general-32)
	arch = any
	bits = 32
endif

ifeq ($(ARCH),x86-32-old)
	arch = i386
	bits = 32
endif

ifeq ($(ARCH),x86-32)
	arch = i386
	bits = 32
	prefetch = yes
	sse = yes
endif

ifeq ($(ARCH),general-64)
	arch = any
endif

ifeq ($(ARCH),x86-64)
	arch = x86_64
	prefetch = yes
	sse = yes

	threadripper = no
endif

ifeq ($(ARCH),x86-64-modern)
	arch = x86_64
	prefetch = yes
	popcnt = yes
	sse = yes
	threadripper = no
endif

ifeq ($(ARCH),x86-64-amd)
	arch = x86_64
	bits = 64
	prefetch = yes
	popcnt = yes

	threadripper = yes
	sse = yes
endif


ifeq ($(ARCH),x86-64-bmi2)
	arch = x86_64
	prefetch = yes
	popcnt = yes
	sse = yes
	pext = yes

	threadripper = no
endif

ifeq ($(ARCH),armv7)
	arch = armv7
	prefetch = yes
	bits = 32
endif

ifeq ($(ARCH),armv8)
	arch = armv8-a
	prefetch = yes
	popcnt = yes
endif

ifeq ($(ARCH),armv7-a)
	arch = any
endif

ifeq ($(ARCH),armv8-a)
	arch = any
	bits = 64
endif

ifeq ($(ARCH),ppc-32)
	arch = ppc
	bits = 32
endif

ifeq ($(ARCH),ppc-64)
	arch = ppc64
	popcnt = yes
	prefetch = yes
endif

### ==========================================================================
### Section 3. Low-level Configuration
### ==========================================================================

### 3.1 Selecting compiler (default = gcc)

CXXFLAGS += -Wall -Wcast-qual -Wno-unused-result -fno-exceptions -std=c++11 $(EXTRACXXFLAGS)
DEPENDFLAGS += -std=c++11
LDFLAGS += $(EXTRALDFLAGS)

ifeq ($(COMP),)
	COMP=gcc
endif

ifeq ($(COMP),gcc)
	comp=gcc
	CXX=g++
	CXXFLAGS += -pedantic -Wextra -Wshadow

	ifeq ($(ARCH),armv7)
	CXXFLAGS += -mcpu=cortex-a53 -mfloat-abi=hard -mfpu=neon-fp-armv8 -mneon-for-64bits -mtune=cortex-a53
		ifeq ($(OS),Android)
			CXXFLAGS += -m$(bits)
			LDFLAGS += -m$(bits)
		endif
	else
		CXXFLAGS += -m$(bits)
		LDFLAGS += -m$(bits)
	endif

	ifneq ($(KERNEL),Darwin)
	   LDFLAGS += -Wl,--no-as-needed
	endif

	gccversion=$(shell gcc --version)
	gccmasqueraded=$(findstring clang,$(gccversion))
endif

ifeq ($(COMP),mingw)
	comp=mingw
	ifeq ($(KERNEL),Linux)
		ifeq ($(bits),64)
			ifeq ($(shell which x86_64-w64-mingw32-c++-posix),)
				CXX=x86_64-w64-mingw32-c++
			else
				CXX=x86_64-w64-mingw32-c++-posix
			endif
		else
			ifeq ($(shell which i686-w64-mingw32-c++-posix),)
				CXX=i686-w64-mingw32-c++
			else
				CXX=i686-w64-mingw32-c++-posix
			endif
		endif
	else
		CXX=g++
	endif

	CXXFLAGS += -Wextra -Wshadow
	LDFLAGS += -static
endif

ifeq ($(COMP),icc)
	comp=icc
	CXX=icpc
	CXXFLAGS += -diag-disable 1476,10120 -Wcheck -Wabi -Wdeprecated -strict-ansi
endif

ifeq ($(COMP),clang)
	comp=clang
	CXX=clang++
	CXXFLAGS += -pedantic -Wextra -Wshadow

	ifneq ($(KERNEL),Darwin)
	ifneq ($(KERNEL),OpenBSD)
		LDFLAGS += -latomic
	endif
	endif

ifeq ($(ARCH),armv7)
		ifeq ($(OS),Android)
			CXXFLAGS += -m$(bits)
			LDFLAGS += -m$(bits)
		endif
	else
		CXXFLAGS += -m$(bits)
		LDFLAGS += -m$(bits)
	endif

	ifeq ($(ARCH),armv8))
		ifeq ($(OS),Android)
			CXXFLAGS += -m$(bits)
			LDFLAGS += -m$(bits)
		endif
	else
		CXXFLAGS += -m$(bits)
		LDFLAGS += -m$(bits)
	endif
endif

### Using NDK pass the path to the NDK using NDK=/path_to_ndk when invoking the makefile
ifeq ($(COMP),ndk)
	comp=clang
	ifeq ($(KERNEL),Linux)
		HOST=linux-x86_64
	endif
	ifeq ($(KERNEL),Darwin)
		HOST=darwin-x86_64
	endif
	CXX=$(NDK)/toolchains/llvm/prebuilt/$(HOST)/bin/clang++

	ifeq ($(ARCH),armv7-a)
		CXXFLAGS += -target armv7a-linux-androideabi21
	endif
	ifeq ($(ARCH),armv8-a)
		CXXFLAGS += -target aarch64-linux-android21
	endif

	CXXFLAGS += -pedantic -Wextra -Wshadow
	LDFLAGS += -static-libstdc++
endif

ifeq ($(comp),icc)
	profile_make = icc-profile-make
	profile_use = icc-profile-use
else
ifeq ($(comp),clang)
	profile_make = clang-profile-make
	profile_use = clang-profile-use
else
	profile_make = gcc-profile-make
	profile_use = gcc-profile-use
endif
endif

ifeq ($(KERNEL),Darwin)
	ifndef MACOSX_DEPLOYMENT_TARGET
	export MACOSX_DEPLOYMENT_TARGET=10.14
	endif
endif

### Travis CI script uses COMPILER to overwrite CXX
ifdef COMPILER
	COMPCXX=$(COMPILER)
endif

### Allow overwriting CXX from command line
ifdef COMPCXX
	CXX=$(COMPCXX)
endif

### On mingw use Windows threads, otherwise POSIX
ifneq ($(comp),mingw)
	# On Android Bionic's C library comes with its own pthread implementation bundled in
	ifneq ($(OS),Android)
	ifneq ($(COMP),ndk)
		# Haiku has pthreads in its libroot, so only link it in on other platforms
		ifneq ($(KERNEL),Haiku)
			LDFLAGS += -lpthread
		endif
	endif
	endif
endif

### 3.2.1 Debugging
ifeq ($(debug),no)
	CXXFLAGS += -DNDEBUG
else
	CXXFLAGS += -g -Wall -Wextra
endif

### 3.2.2 Debugging with undefined behavior sanitizers
ifneq ($(sanitize),no)
        CXXFLAGS += -g3 -fsanitize=$(sanitize) -fuse-ld=gold
        LDFLAGS += -fsanitize=$(sanitize) -fuse-ld=gold
endif

### 3.3 Optimization
ifeq ($(optimize),yes)

	CXXFLAGS += -O3

	ifeq ($(comp),gcc)
		ifeq ($(OS), Android)
			CXXFLAGS += -fno-gcse -mthumb -march=armv7-a -mfloat-abi=softfp
		endif
	endif

	ifeq ($(comp),$(filter $(comp),gcc clang icc))
		ifeq ($(KERNEL),Darwin)
			CXXFLAGS += -mdynamic-no-pic
		endif
	endif
endif

### 3.4 Bits
ifeq ($(bits),64)
	CXXFLAGS += -DIS_64BIT
endif

### 3.5 prefetch
ifeq ($(prefetch),yes)
	ifeq ($(sse),yes)
		CXXFLAGS += -msse
		DEPENDFLAGS += -msse
	endif
else
	CXXFLAGS += -DNO_PREFETCH
endif

### 3.6 popcnt
ifeq ($(popcnt),yes)
	ifeq ($(arch),$(filter $(arch),ppc64 armv8-a))
		CXXFLAGS += -DUSE_POPCNT
	else ifeq ($(comp),icc)
		CXXFLAGS += -msse4 -DUSE_POPCNT
	else
		CXXFLAGS += -msse4 -mpopcnt -DUSE_POPCNT
	endif
endif

### 3.6a tr -AMD -LargePages
ifeq ($(threadripper),yes)
	CXXFLAGS += --param l1-cache-line-size=2048 -l2-cache-size=16384 -l3-cache-size=131072
	### since we do not use native with a Threadripper to avoid bmi2
	ifeq ($(comp),$(filter $(comp),gcc clang mingw))
		CXXFLAGS += -msse4.1 -msse4a -mbmi
	endif
endif

### 3.7 pext
ifeq ($(pext),yes)
	CXXFLAGS += -DUSE_PEXT
	ifeq ($(comp),$(filter $(comp),gcc clang mingw))
		CXXFLAGS += -msse4 -mbmi2
	endif
endif

### 3.8 Link Time Optimization
### This is a mix of compile and link time options because the lto link phase
### needs access to the optimization flags.
ifeq ($(optimize),yes)
ifeq ($(debug), no)
	ifeq ($(comp),clang)
		CXXFLAGS += -flto
		LDFLAGS += $(CXXFLAGS)
	endif

	ifeq ($(comp),gcc)
		CXXFLAGS += -flto
	ifeq ($(gccmasqueraded),)
		LDFLAGS += $(CXXFLAGS) -flto=jobserver
	else
		LDFLAGS += $(CXXFLAGS)
	endif
	endif

	ifeq ($(comp),mingw)
	ifeq ($(KERNEL),Linux)
		CXXFLAGS += -flto
		LDFLAGS += $(CXXFLAGS) -flto=jobserver
	endif
	endif
endif
endif

### 3.9 Android 5 can only run position independent executables. Note that this
### breaks Android 4.0 and earlier.
ifeq ($(OS), Android)
	CXXFLAGS += -fPIE
	LDFLAGS += -fPIE -pie
endif
ifeq ($(ARCH), $(filter $(ARCH), armv7-a armv8-a))
	CXXFLAGS += -fPIE
	LDFLAGS += -fPIE -pie
endif
### 3.10 madvise + transparent huge pages
ifeq ($(KERNEL),Linux)
	ifneq ($(ARCH), $(filter $(ARCH), armv7-a armv8-a))
		CXXFLAGS += -DUSE_MADVISE_HUGEPAGE
	endif
endif

### strip executable
ifeq ($(COMP), ndk)
	ifeq ($(ARCH),armv7-a)
		SUB_DIR=arm-linux-androideabi
	endif
	ifeq ($(ARCH),armv8-a)
		SUB_DIR=aarch64-linux-android
	endif
	STRIP=$(NDK)/toolchains/llvm/prebuilt/$(HOST)/$(SUB_DIR)/bin/strip
else
	STRIP=strip
endif
### ==========================================================================
### Section 4. Public Targets
### ==========================================================================

help:
	@echo ""
	@echo "To compile Honey, type: "
	@echo "'make <target> ARCH=arch [COMP=compiler] [COMPCXX=cxx]'"
	@echo "<target> would be 'build' or 'profile-build'"
	@echo ""
	@echo "To compile stockfish, uncomment this line in the makefile: "
	@echo "'### HONEY=yes' by remvoing the 3 #(pound signs)"
	@echo "then type: 'make <target> ARCH=<arch> [COMP=compiler] [COMPCXX=cxx]'"
	@echo ""
	@echo "Supported targets:"
	@echo ""
	@echo "build                   > Standard build"
	@echo "profile-build           > PGO build"
	@echo "strip                   > Strip executable"
	@echo "install                 > Install executable"
	@echo "clean                   > Clean up"
	@echo ""
	@echo "Supported archs:"
	@echo ""
	@echo "x86-64-bmi2             > x86 64-bit with pext support (also enables SSE4)"
	@echo "x86-64-modern           > x86 64-bit with popcnt support (also enables SSE3)"
	@echo "x86-64                  > x86 64-bit generic"
	@echo "x86-32                  > x86 32-bit (also enables SSE)"
	@echo "x86-32-old              > x86 32-bit fall back for old hardware"
	@echo "ppc-64                  > PPC 64-bit"
	@echo "ppc-32                  > PPC 32-bit"
	@echo "armv7                   > ARMv7 32-bit"
	@echo "armv8                   > ARMv8 64-bit"
	@echo "general-64              > unspecified 64-bit"
	@echo "general-32              > unspecified 32-bit"
	@echo ""
	@echo "Supported compilers:"
	@echo ""
	@echo "gcc                     > Gnu compiler (default)"
	@echo "mingw                   > Gnu compiler with MinGW under Windows"
	@echo "clang                   > LLVM Clang compiler"
	@echo "icc                     > Intel compiler"
	@echo ""
	@echo "Simple examples. If you don't know what to do, you likely want to run: "
	@echo ""
	@echo "make build ARCH=x86-64    (This is for 64-bit systems)"
	@echo "make build ARCH=x86-32    (This is for 32-bit systems)"
	@echo ""
	@echo "Advanced examples, for experienced users: "
	@echo ""
	@echo "make build ARCH=x86-64 COMP=clang"
	@echo "make build ARCH=armv8-a COMP=ndk NDK=~/android-ndk-r21"
	@echo "make profile-build ARCH=x86-64-bmi2 COMP=gcc COMPCXX=g++-4.8"
	@echo ""

directory = ../bench_nodes
all: | $(directory)
$(directory):
	mkdir -p $@


.PHONY: help build profile-build strip install clean objclean profileclean \
        config-sanity icc-profile-use icc-profile-make gcc-profile-use gcc-profile-make \
        clang-profile-use clang-profile-make

build: config-sanity
	@$(MAKE) ARCH=$(ARCH) COMP=$(COMP) all
	@$(STRIP) $(EXE)
	@rm -f *.o syzygy/*.o

profile-build: config-sanity objclean profileclean
	@echo ""
	@echo "Step 1/4. Building instrumented executable ..."
	@$(MAKE) ARCH=$(ARCH) COMP=$(COMP) $(profile_make)
	@echo ""
	@echo "Step 2/4. Running benchmark for pgo-build ..."
	@$(PGOBENCH)  >/dev/null  && wait
	@$(PGOBENCH2) >/dev/null  && wait
	@echo ""
	@echo "Step 3/4. Building optimized executable ..."
	@$(MAKE) ARCH=$(ARCH) COMP=$(COMP) objclean
	@$(MAKE) ARCH=$(ARCH) COMP=$(COMP) $(profile_use)
	@echo ""
	@echo "Step 4/4. Deleting profile data ..."
	@$(MAKE) ARCH=$(ARCH) COMP=$(COMP) profileclean
##ifeq ($(COMP),mingw)
##	strip $(EXE)
##else
##	strip $(EXE)
##endif

ifeq ($(COMP),mingw)
	$(EXE) bench >/dev/null 2> $(EXE).bench && wait
endif
	rm -f *.o syzygy/*.o llvm-profdata
#	touch * syzygy/*
#	cp $(EXE) /opt/picochess/engines/armv7l
	@echo ""
	@echo "==================================="
	@echo "$(EXE) build completed..."
	@echo "==================================="
	@echo ""

strip:
	$(STRIP) $(EXE)

install:
	-mkdir -p -m 755 $(BINDIR)
	-cp $(EXE) $(BINDIR)
	-strip $(BINDIR)/$(EXE)

#clean all
clean: objclean profileclean
	@rm -f .depend *~ core

# clean binaries and objects
objclean:
	@rm -f $(EXE) *.o ./syzygy/*.o

# clean auxiliary profiling files
profileclean:
	@rm -rf profdir
	@rm -f bench.txt *.gcda ./syzygy/*.gcda *.gcno ./syzygy/*.gcno
	@rm -f stockfish.profdata *.profraw

default:
	help

### ==========================================================================
### Section 5. Private Targets
### ==========================================================================

all: $(EXE) .depend

config-sanity:
	@echo ""
	@echo "Config:"
	@echo "debug: '$(debug)'"
	@echo "sanitize: '$(sanitize)'"
	@echo "optimize: '$(optimize)'"
	@echo "arch: '$(arch)'"
	@echo "bits: '$(bits)'"
	@echo "kernel: '$(KERNEL)'"
	@echo "os: '$(OS)'"
	@echo "prefetch: '$(prefetch)'"
	@echo "popcnt: '$(popcnt)'"
	@echo "sse: '$(sse)'"
	@echo "pext: '$(pext)'"
	@echo ""
	@echo "Flags:"
	@echo "CXX: $(CXX)"
	@echo "CXXFLAGS: $(CXXFLAGS)"
	@echo "LDFLAGS: $(LDFLAGS)"
	@echo ""
	@echo "Testing config sanity. If this fails, try 'make help' ..."
	@echo ""
	@test "$(debug)" = "yes" || test "$(debug)" = "no"
	@test "$(sanitize)" = "undefined" || test "$(sanitize)" = "thread" || test "$(sanitize)" = "address" || test "$(sanitize)" = "no"
	@test "$(optimize)" = "yes" || test "$(optimize)" = "no"
	@test "$(arch)" = "any" || test "$(arch)" = "x86_64" || test "$(arch)" = "i386" || \
	@test "$(arch)" = "ppc64" || test "$(arch)" = "ppc" || "$(arch)" = "armv7" || test "$(arch)" = "armv8-a"
	@test "$(bits)" = "32" || test "$(bits)" = "64"
	@test "$(prefetch)" = "yes" || test "$(prefetch)" = "no"
	@test "$(popcnt)" = "yes" || test "$(popcnt)" = "no"
	@test "$(sse)" = "yes" || test "$(sse)" = "no"
	@test "$(pext)" = "yes" || test "$(pext)" = "no"
	@test "$(comp)" = "gcc" || test "$(comp)" = "icc" || test "$(comp)" = "mingw" || test "$(comp)" = "clang"

$(EXE): $(OBJS)
	$(CXX) -o $@ $(OBJS) $(LDFLAGS)

clang-profile-make:
	$(MAKE) ARCH=$(ARCH) COMP=$(COMP) \
	EXTRACXXFLAGS='-fprofile-instr-generate ' \
	EXTRALDFLAGS=' -fprofile-instr-generate' \
	all

clang-profile-use:
	/opt/local/bin/llvm-profdata-mp-7.0 merge -output=stockfish.profdata *.profraw
	$(MAKE) ARCH=$(ARCH) COMP=$(COMP) \
	EXTRACXXFLAGS='-fprofile-instr-use=stockfish.profdata -Wno-profile-instr-out-of-date' \
	EXTRALDFLAGS='-fprofile-use ' \
	all

gcc-profile-make:
	$(MAKE) ARCH=$(ARCH) COMP=$(COMP) \
	EXTRACXXFLAGS='-fprofile-generate -fprofile-correction' \
	EXTRALDFLAGS='-lgcov' \
	all

gcc-profile-use:
	$(MAKE) ARCH=$(ARCH) COMP=$(COMP) \
	EXTRACXXFLAGS='-fprofile-use -fprofile-correction -fno-peel-loops -fno-tracer' \
	EXTRALDFLAGS='-lgcov' \
	all

icc-profile-make:
	@mkdir -p profdir
	$(MAKE) ARCH=$(ARCH) COMP=$(COMP) \
	EXTRACXXFLAGS='-prof-gen=srcpos -prof_dir ./profdir' \
	all

.depend:
	-@$(CXX) $(DEPENDFLAGS) -MM $(OBJS:.o=.cpp) > $@ 2> /dev/null

-include .depend
#
#
#
#
#
#
#
#
#
#
#
#
#
### Based on commits through 07/03/2020:
### ======================================================
### Black-Diamond-XI-r3.exe.bench:Nodes searched  : 15038924
### Black-Diamond-XI-r3.exe.bench:Nodes/second    : 2294967
### Bluefish-XI-r3.exe.bench:Nodes searched  : 4377334
### Bluefish-XI-r3.exe.bench:Nodes/second    : 2019065
### Honey-XI-r3.exe.bench:Nodes searched  : 4564579
### Honey-XI-r3.exe.bench:Nodes/second    : 2596461
### Stockfish-XI-r3.exe.bench:Nodes searched  : 4431626
### Stockfish-XI-r3.exe.bench:Nodes/second    : 2481313
### Weakfish-XI-r3.exe.bench:Nodes searched  : 4728
### Weakfish-XI-r3.exe.bench:Nodes/second    : 236400
### ======================================================
