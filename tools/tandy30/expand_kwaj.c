/*
 * Small KWAJ extractor using libmspack.
 * Microsoft Mouse 9.01 ships MOUSE.DR$ in KWAJ, not a ZIP or CAB member.
 */
#include <mspack.h>
#include <stdio.h>

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s input.dr$ output.drv\n", argv[0]);
        return 2;
    }
    struct mskwaj_decompressor *d = mspack_create_kwaj_decompressor(NULL);
    if (!d) {
        fputs("Unable to initialize libmspack KWAJ decompressor\n", stderr);
        return 3;
    }
    int rc = d->decompress(d, argv[1], argv[2]);
    if (rc != MSPACK_ERR_OK) {
        fprintf(stderr, "KWAJ decompression failed, libmspack error %d\n", rc);
    }
    mspack_destroy_kwaj_decompressor(d);
    return rc == MSPACK_ERR_OK ? 0 : 4;
}
