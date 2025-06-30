    .syntax unified

#include "version.h"

    .section .header, "a"

    .type g_header, %object
    .size g_header, .-g_header

g_header:
    .byte 'T','R','Z','Q'              // magic
    .word HW_MODEL                     // type of the designated hardware
    .word HW_REVISION                  // revision of the designated hardware
    .byte VERSION_MAJOR                // vmajor
    .byte VERSION_MINOR                // vminor
    .byte VERSION_PATCH                // vpatch
    .byte VERSION_BUILD                // vbuild
    .byte FIX_VERSION_MAJOR            // fix_vmajor
    .byte FIX_VERSION_MINOR            // fix_vminor
    .byte FIX_VERSION_PATCH            // fix_vpatch
    .byte FIX_VERSION_BUILD            // fix_vbuild
    .word BOOTLOADER_MONOTONIC_VERSION // monotonic version of the binary
    .word g_header_end - g_header      // header_size
    .word _codelen                     // code_size

    . = . + 608                        // reserved
    . = . + 7856                       // signature 1
    . = . + 7856                       // signature 2
    . = . + 32                         // reserved
g_header_end:
