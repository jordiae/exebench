from datasets import load_dataset
from exebench import Wrapper, diff_io, exebench_dict_to_dict


def main():
    # 1) Load dataset split. In this case, synthetic test split
    dataset = load_dataset('jordiae/exebench', split='test_synth') # , use_auth_token=True)
    # 2) Iterate over dataset
    for row in dataset:
        # Do stuff with each row
        # 3) Option A: Manually access row fields. For instance, access the function definition:
        print(row['func_head_types'])
        print(row['func_def'])  # print function definition
        print(row['asm']['code'][0])  # print assembly with the first target, angha_gcc_x86_O0
        # print first I/O example (synthetic)
        print('Input:', exebench_dict_to_dict(row['synth_io_pairs']['input'][0]))
        print('Output:', exebench_dict_to_dict(row['synth_io_pairs']['output'][0]))
        print(row['synth_exe_wrapper'][0])  # print C++ wrapper to run function with IO
        # You can manually compile, run with IO, etc
        # TODO! somethimes row['func_head'] is not OK!
        # 3) Option B: Use ExeBenchFunc wrapper.
        try:
            synth_wrapper = Wrapper(c_deps=row['synth_deps'] + '\n' + row['synth_io_pairs']['dummy_funcs'][0] + '\n',
                                    func_c_signature=row['func_head_types'].replace('extern', ''), func_assembly=row['asm']['code'][0],
                                    cpp_wrapper=row['synth_exe_wrapper'])
            observed_output = synth_wrapper(exebench_dict_to_dict(row['synth_io_pairs']['input'][0]))  # Run synthetic example number 0
            print('Input', exebench_dict_to_dict(row['synth_io_pairs']['input'][0]))
            print('Observed Output:', observed_output)
            print('Does this output coincide with the expected one?',
                  'Yes' if diff_io(observed_output=observed_output,
                                   expected_output=exebench_dict_to_dict(row['synth_io_pairs']['output'][0])) else 'No')
        except:
            # Very occasionally the compilating using func_assembly=row['asm']['code'][0] seems to fail.
            # My best guess at this moment is that the self-contained function assembly is not "self-contained enough"
            # in a few cases, and in these cases it's better to recompile everything and run it all together.
            # TODO: fix, or find a better explanation
            pass

        # Run with custom IO (variable names must match:
        # inp = {'a': 3, ...}

        break


if __name__ == '__main__':
    main()
