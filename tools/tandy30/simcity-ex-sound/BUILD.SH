#!/bin/sh
set -eu
cd "$(dirname "$0")"
as --32 -o SCEXSND.o SCEXSND.S
ld -m elf_i386 -Ttext 0x100 -e start --oformat binary -o SCEXSND.COM SCEXSND.o
as --32 -o TESTSND.o TESTSND.S
ld -m elf_i386 -Ttext 0x100 -e start --oformat binary -o TESTSND.COM TESTSND.o
as --32 -o TSRPROBE.o TSRPROBE.S
ld -m elf_i386 -Ttext 0x100 -e start --oformat binary -o TSRPROBE.COM TSRPROBE.o
rm -f SCEXSND.o TESTSND.o TSRPROBE.o
printf 'Built: '; wc -c SCEXSND.COM TESTSND.COM TSRPROBE.COM
