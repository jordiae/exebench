unsigned int reverseBits(unsigned int num, unsigned int no_bits)
{
    unsigned int reverse_num = 0, temp;

	while (no_bits > 1)
    {
		reverse_num = reverse_num << 1;
		reverse_num = reverse_num | (num & 1);

		// Shrink.
		no_bits = no_bits >> 1;
		num = num >> 1;
    }

    return reverse_num;
}
