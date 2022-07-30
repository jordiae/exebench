#include <stddef.h>
#include <stdint.h> // TODO -- this may not be enough on some platforms for uintptr?  Can we just use long long safetly?
#include <stdlib.h>
#include "synthesizer.h"

// We need to keep track of the differences that are 
// added to each pointer to align them so we can 
// free them properly.

// Fortunately, this is easier to write than
// it might otherwise be because if an accelerator
// has N malloc-able arguments, then the most we
// are going to be malloc-ing is N + 1 (for the
// return value.  FFTs tend to have two (in and out)
// but four is not implausible (in real, out real,
// in imag, out imag).  Anyway, so we'll just
// support like 8 for now, and segfault if there
// are more.

int facc_malloc_count = 0;
typedef struct {
	uintptr_t returned;
	uintptr_t original;
} pointer_map_pair;

pointer_map_pair pointer_map[8];

// An aligned malloc and free function.
// Note that if an aligned malloc escapes the
// accelerated function, then all frees that are
// reachable by that pointer must be replaced with
// facc_free.
void *facc_malloc(size_t alignment, size_t size) {
	char* ptr = (char*) malloc(size + alignment);

	uintptr_t original_pointer = (uintptr_t) ptr;
	uintptr_t offset_pointer = original_pointer;
	if (alignment != 0) {
		offset_pointer += (original_pointer % alignment);
		// If the offset is zero, we don't have to use
		// the facc malloc.  Really, we should do
		// this statically in FACC (i.e. turn into a normal
		// malloc)
		pointer_map[facc_malloc_count].original = original_pointer;
		pointer_map[facc_malloc_count].returned = offset_pointer;
		facc_malloc_count += 1;
	}

	return (void*) offset_pointer;
}

// This could really be much more efficient IMO.
void facc_free(void* pointer) {
	uintptr_t pointer_value = (uintptr_t) pointer;
	for (int i = 0; i < facc_malloc_count; i ++) {
		if (pointer_map[i].returned == pointer_value) {
			free((void *) pointer_map[i].original);

			// Shuffle everyting back down
			for (int j = i; j < facc_malloc_count - 1; j ++) {
				pointer_map[j] = pointer_map[j + 1];
			}

			facc_malloc_count --;
			return;
		}
	}

	free(pointer);
}

void facc_strcopy(char *str_in, char *str_out) {
	while (*str_in != '\0') {
		*str_out = *str_in;
		str_in ++;
		str_out ++;
	}
	// Copy the null terminating character too.
	*str_out = *str_in;
}
