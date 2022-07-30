#include <assert.h>
#include "../fft_synth/lib.h"
#include <stdio.h>

int main() {
	assert(reverseBits(1, 8) == 4);
	assert(reverseBits(2, 8) == 2);

	int arr[8] = {0, 1, 2, 3, 4, 5, 6, 7};

	BIT_REVERSE(arr, 8);

	printf("Array is %d, %d, %d, %d, %d, %d, %d, %d\n", arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6], arr[7]);

	assert(arr[0] == 0);
	assert(arr[1] == 4);
	assert(arr[2] == 2);
	assert(arr[3] == 6);
}
