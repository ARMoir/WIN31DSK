#!/bin/sh
set -eu
cd "$(dirname "$0")"
as --32 -o SCEXSND.o SCEXSND.S
ld -m elf_i386 -Ttext 0x100 -e start --oformat binary -o SCEXSND.COM SCEXSND.o
as --32 -o TESTSND.o TESTSND.S
ld -m elf_i386 -Ttext 0x100 -e start --oformat binary -o TESTSND.COM TESTSND.o
as --32 -o TSRPROBE.o TSRPROBE.S
ld -m elf_i386 -Ttext 0x100 -e start --oformat binary -o TSRPROBE.COM TSRPROBE.o
for name in HOOK1A HOOK1C; do
  as --32 -o "$name.o" "$name.S"
  ld -m elf_i386 -Ttext 0x100 -e start --oformat binary -o "$name.COM" "$name.o"
done
as --32 -o SCGATE.o SCGATE.S
ld -m elf_i386 -Ttext 0x100 -e start --oformat binary -o SCGATE.COM SCGATE.o
rm -f TSRPROBE.o HOOK1A.o HOOK1C.o SCGATE.o
printf 'Built: '; wc -c SCEXSND.COM TESTSND.COM TSRPROBE.COM HOOK1A.COM HOOK1C.COM SCGATE.COM
