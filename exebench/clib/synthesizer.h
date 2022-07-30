#include <stddef.h>

// Conditions
#define POWER_OF_TWO(x) ((x & (x - 1)) == 0)
#define GREATER_THAN(x, y) x > y
#define GREATER_THAN_OR_EQUAL(x, y) x >= y
#define LESS_THAN(x, y) x < y
#define LESS_THAN_OR_EQUAL(x, y) x <= y
#define PRIM_EQUAL(x, y) x == y
/* TODO --- would like to make this better.  */
#define FLOAT_EQUAL(x, y) ((x < y + x / 1000.0) && (x > y - x / 1000.0))

// Operations
#define Pow2(x) (1 << x)
#define IntDivide(x,y) (x / y)

#define Multiply(x, y) (x * y)

// Strings are internally dimensionless, but if they need
// to be alloated in C we need to decide on the amount
// of space they require.  One expects this to be platform
// and application dependent (and really to be changed
// to an appropriate value by the programmer).
#define MAX_STRING_SIZE 2048

// Builtin types
typedef struct { float f32_1; float f32_2; } facc_2xf32_t;
typedef struct { float f64_1; float f64_2; } facc_2xf64_t;

// FACC aligned memory functions
void *facc_malloc(size_t alignment, size_t size);
void facc_free(void* pointer);

// Generic utility functions
void facc_strcopy(char *str_in, char *str_out);
