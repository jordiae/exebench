from datasets import load_dataset
from exebench import Wrapper, diff_io, exebench_dict_to_dict

def main2():
    # 1) Load dataset split. In this case, synthetic test split
    dataset = load_dataset('jordiae/exebench', split='test_synth', use_auth_token=True)
    # 2) Iterate over dataset
    for row in dataset:
        # Do stuff with each row
        # 3) Option A: Manually access row fields. For instance, access the function definition:
        print(row['func_def'])  # print function definition
        print(row['asm']['code'][0])  # print assembly with the first target, angha_gcc_x86_O0
        # print first I/O example (synthetic)
        print('Input:', row['synth_io_pairs']['input'][0])
        print('Output:', row['synth_io_pairs']['output'][0])
        print(row['synth_exe_wrapper'][0])  # print C++ wrapper to run function with IO
        # You can manually compile, run with IO, etc
        # TODO! somethimes row['func_head'] is not OK!
        # 3) Option B: Use ExeBenchFunc wrapper.
        synth_wrapper = Wrapper(c_deps=row['synth_deps'], func_c_signature=row['func_head'], func_assembly=row['asm']['code'][0],
                                cpp_wrapper=row['synth_exe_wrapper'])
        observed_output = synth_wrapper(exebench_dict_to_dict(row['synth_io_pairs']['input'][0]))  # Run synthetic example number 0
        print('Input', row['synth_io_pairs']['input'][0])
        print('Expected Output:', observed_output)
        print('Does this output coincide with the expected one?',
              'Yes' if diff_io(observed_output=observed_output,
                               expected_output=row['synth_io_pairs']['output'][0]) else 'No')
        # Run with custom IO (variable names must match:
        # inp = {'a': 3, ...}
        # exebench_func_wrapper(inp)

def main():
    # 1) Load dataset split. In this case, synthetic validation split
    dataset = load_dataset('jordiae/exebench', split='valid_synth', use_auth_token=True)
    # 2) Iterate over dataset
    for row in dataset:
        # Do stuff with each row
        # 3) Option A: Manually access row fields. For instance, access the function definition:
        print(row['func_def'])  # print function definition
        print(row['asm']['code'][0])  # print assembly with the first target, angha_gcc_x86_O0
        print(row['synth_io_pairs'][0])  # print first I/O example (synthetic)
        print(row['synth_exe_wrapper'][0])  # print C++ wrapper to run function with IO
        # You can manually compile, run with IO, etc

        # 3) Option B: Use ExeBenchFunc wrapper.
        exebench_func_wrapper = ExeBenchFunc(row)
        observed_output = exebench_func_wrapper.run_row_real_io(row['synth_io_pairs']['input'][0])  # Run synthetic example number 0
        print('Input', row['synth_io_pairs']['input'][0])
        print('Expected Output:', observed_output)
        print('Does this output coincide with the expected one?',
              'Yes' if diff_io(observed_output=observed_output, expected_output=row['synth_io_pairs']['output'][0]) else 'No')
        # Run with custom IO (variable names must match:
        # inp = {'a': 3, ...}
        # exebench_func_wrapper(inp)


if __name__ == '__main__':
    main2()
