from typing import Dict, Optional, List
import operator
import itertools
from dataclasses import asdict, dataclass
import sh
from dataclasses import dataclass, asdict
from abc import ABC
from koda import Ok, Err, Result
import re
import json
import math


# For the moment, don't support MASM


@dataclass
class AsmTarget:
    impl: str
    bits: int
    lang: str
    o: str

    def __post_init__(self):
        assert self.impl in ['gcc', 'clang']
        assert self.bits in [32, 64]
        assert self.lang in ['masm', 'gas', 'llvm']
        assert self.o in ['0', '1', '2', '3', 'fast', 'g', 'fast', 's']

    def dict(self):
        return asdict(self)


@dataclass
class FuncAsm:
    pre_asm: str  # asm directives before, and also e.g. global variable declarations needed to compile llvm functions
    func_asm: str  # asm of function itself
    post_asm: str  # asm directives after the function itself
    target: AsmTarget

    def dict(self):
        return asdict(self)


class Compiler:
    def __init__(self, arch, o, lang, bits=64):
        self.arch = arch
        self.o = o
        self.bits = bits
        self.lang = lang

    def get_func_asm(self, all_required_c_code, fname, output_path=None) -> Result[FuncAsm, BaseException]:
        return self._get_func_asm(all_required_c_code, fname, output_path, arch=self.arch, o=self.o, bits=self.bits)

    def _get_func_asm(self, all_required_c_code, fname, output_path, arch, o, bits) -> Result[FuncAsm, BaseException]:
        raise NotImplementedError

    def _asm_replace_constants_with_literals(self, all_asm, func_asm):
        raise NotImplementedError

    @classmethod
    def factory(cls, impl, *args, **kwargs):
        if impl == 'gcc':
            return GCC(*args, **kwargs)
        elif impl == 'clang':
            return Clang(*args, **kwargs)
        raise NotImplementedError(f'impl = {impl}')


class GASCompiler(ABC, Compiler):

    def get_comment_sym(self):
        if self.lang == 'gas':
            if self.arch == 'arm':
                return '@'
            return '#'
        elif self.lang == 'llvm':
            return ';'
        else:
            raise ValueError(f'lang = {self.lang}')

    def _asm_replace_constants_with_literals(self, all_asm, func_asm):
        all_asm = all_asm.decode("utf-8")
        asm_to_add = []
        for symbol in re.compile('\.LC[0-9]*').findall(func_asm):  # TODO: move, compile once
            for e in re.findall(f'\.{symbol.replace(".", "")}:[\r\n]+([^\r\n]+)', all_asm):
                asm_to_add.append(symbol + ': ' + e)
                break
        for symbol in re.compile('a\.[0-9]*').findall(func_asm):  # TODO: move, compile once
            for e in re.findall(f'{symbol}:[\r\n]+([^\r\n]+)', all_asm):
                asm_to_add.append(symbol + ': ' + e)
                break
        return func_asm + '\n' + '\n'.join(asm_to_add) + '\n'

    def _gas_get_func_asm_from_all_asm(self, fname, all_asm):

        def strip_comments(code, comment_sym):  # only support simple commands, asm
            res = []
            for l in code.splitlines():
                without_comments = l.split(comment_sym)[0]
                if len(without_comments.split()) > 0:
                    res.append(without_comments)
            return '\n'.join(res)

        func = [f'.globl {fname}', f'.type {fname}, @function']
        inside_func = False
        after_func = False
        pre_asm = []
        post_asm = []
        for l in all_asm.splitlines():
            if l.startswith(f'{fname}:'):
                inside_func = True
            if inside_func:
                func.append(l)
            elif after_func:
                post_asm.append(l)
            else:
                if f'.globl {fname}' not in l:
                    pre_asm.append(l)
            if inside_func and '.cfi_endproc' in l:
                inside_func = False
                after_func = True

        pre_asm = '\n'.join(pre_asm) + '\n'
        func_asm = '\n'.join(func) + '\n'
        comment_sym = self.get_comment_sym()
        func_asm = strip_comments(func_asm, comment_sym=comment_sym)
        post_asm = '\n'.join(post_asm) + '\n'

        return pre_asm, func_asm, post_asm


class GCC(GASCompiler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, lang='gas', **kwargs)
        self.arm_64 = sh.aarch64_linux_gnu_gcc  # sudo apt install aarch64-linux-gnu-gcc
        self.x86_64 = sh.gcc

    def _get_func_asm(self, all_required_c_code, fname, output_path, arch, o, bits) -> Result[FuncAsm, BaseException]:
        lang = 'gas'  # we don't support masm
        if arch == 'arm' and bits == 64:
            backend = self.arm_64
        elif arch == 'x86' and bits == 64:
            backend = self.x86_64
        else:
            raise NotImplementedError(f'arch = {arch}, bits = {bits}')
        try:
            out = backend('-S', f'-O{o}', '-x', 'c', '-o', '/dev/stdout', '-', _in=all_required_c_code)
        except BaseException as e:
            return Err(e)

        pre_asm, func_asm, post_asm = self._gas_get_func_asm_from_all_asm(all_asm=out, fname=fname)
        func_asm = self._asm_replace_constants_with_literals(all_asm=out.stdout, func_asm=func_asm)
        func_asm = FuncAsm(pre_asm=pre_asm, func_asm=func_asm, post_asm=post_asm, target=AsmTarget(impl='gcc',
                                                                                                   bits=bits,
                                                                                                   lang=lang,
                                                                                                   o=o))
        return Ok(func_asm)


class Clang(GASCompiler):
    def __init__(self, *args, emit_llvm=False, **kwargs):
        lang = 'llvm' if emit_llvm else 'gas'
        super().__init__(*args, lang=lang, **kwargs)
        self.clang = sh.clang  # sudo apt install clang
        self.emit_llvm = emit_llvm
        self.emit_llvm_flag = '-emit-llvm' if emit_llvm else ''

    def _get_func_asm(self, all_required_c_code, fname, output_path, arch, o, bits) -> Result[FuncAsm, BaseException]:
        if arch == 'x86' and bits == 64:
            backend = self.clang
        else:
            raise NotImplementedError(f'arch = {arch}, bits = {bits}')
        try:
            out = backend('-S', self.emit_llvm_flag, f'-O{o}', '-x', 'c', '-o', '/dev/stdout', '-',
                          _in=all_required_c_code)
        except BaseException as e:
            return Err(e)
        try:
            if self.emit_llvm:
                pre_asm, func_asm, post_asm = self._llvm_get_func_asm_from_all_asm(all_asm=out, fname=fname)
            else:
                pre_asm, func_asm, post_asm = self._gas_get_func_asm_from_all_asm(all_asm=out, fname=fname)
        except RuntimeError as e:
            return Err(e)
        func_asm = self._asm_replace_constants_with_literals(all_asm=out.stdout, func_asm=func_asm)
        func_asm = FuncAsm(pre_asm=pre_asm, func_asm=func_asm, post_asm=post_asm, target=AsmTarget(impl='clang',
                                                                                                   bits=bits,
                                                                                                   lang='llvm' if self.emit_llvm else 'gas',
                                                                                                   o=o))
        return Ok(func_asm)

    @staticmethod
    def _llvm_get_func_asm_from_all_asm(fname, all_asm):
        # @var = common dso_local global i32 0, align 4
        # ; Function Attrs: noinline nounwind optnone uwtable
        # define dso_local i32 @f(i32 %0) #0 {
        func = []
        inside_func = False
        after_func = False
        pre_asm = []
        post_asm = []
        for l in all_asm.splitlines():
            if l.startswith('define') and f'@{fname}(' in l:
                inside_func = True
            if inside_func:
                func.append(l)
            elif after_func:
                post_asm.append(l)
            else:
                pre_asm.append(l)
            # if inside_func and 'ret' in l.split():  # Todo: not always ret
            if inside_func and l.startswith('}'):
                inside_func = False
                after_func = True
        func.append('}')
        if len(post_asm) == 0:
            raise RuntimeError("Couldn't process assembly")
        del post_asm[0]

        pre_asm = '\n'.join(pre_asm) + '\n'
        func_asm = '\n'.join(func) + '\n'
        post_asm = '\n'.join(post_asm) + '\n'

        return pre_asm, func_asm, post_asm


# TODO: literals/constats, global variables etc in LLVM, clang etc


@dataclass
class IOPair:
    input: Dict
    output: Dict
    dummy_funcs: Optional[str] = None
    dummy_funcs_seed: Optional[int] = None

    def dict(self):
        return asdict(self)

    @classmethod
    def group_by_seed(cls, iopairs: List['IOPair']):
        get_attr = operator.attrgetter('dummy_funcs_seed')
        grouped_by = [list(g) for k, g in itertools.groupby(sorted(iopairs, key=get_attr), get_attr)]
        return grouped_by


@dataclass
class FuncDataclass:
    path: str
    func_def: str
    func_head: str
    fname: str
    signature: List[str]
    doc: Optional[str] = None
    angha_error: Optional[str] = None
    real_error: Optional[str] = None
    # TODO: fname, signature (without parnames)
    asm: Optional[Dict[str, Optional[FuncAsm]]] = None
    angha_deps: Optional[str] = None
    real_deps: Optional[str] = None
    angha_io_pairs: List[IOPair] = None
    real_io_pairs: List[IOPair] = None
    angha_io_error: Optional[str] = None
    real_io_error: Optional[str] = None
    angha_exe_wrapper: Optional[str] = None
    real_exe_wrapper: Optional[str] = None
    angha_io_pairs_are_trivial: bool = False
    real_io_pairs_are_trivial: bool = False
    angha_iospec: Optional[Dict] = None
    real_iospec: Optional[Dict] = None
    ref: str = 'master'

    def dict(self):
        return asdict(self)

    def get_fname_tmp_fix(self):
        return self.func_head.split('(')[-2].split()[-1].replace('*', '')

    @classmethod
    def legacy_init(cls, **kwargs):
        del kwargs['io_pairs']
        return cls(**kwargs)


def run():
    gpp = GPP(print_stderr=True)
    compiled_wrapper_output_path = wrapper_path.replace('.cpp', '.x')  # os.path.join('wrapper')
    gpp.compile_exe_to_file(open(wrapper_path, 'r').read(), path=compiled_wrapper_output_path)

    # 5: Run IO

    io_pairs = []
    for json_file in sorted(glob(os.path.join(io_path, 'io', '1', '*.json'))):
        output_file = ''.join(json_file.split(".")[:1]) + '-out.json'
        stdout, stderr = run_command(f'{compiled_wrapper_output_path} {json_file} {output_file}')
        if fast_sanity_check:
            if not stderr or len(stderr) == 0:
                output_file_check = ''.join(json_file.split(".")[:1]) + '-out-check.json'
                stdout, stderr = run_command(f'{compiled_wrapper_output_path} {json_file} {output_file_check}')
            else:
                raise IOGenerationError
        with open(json_file, 'r') as f1, open(output_file, 'r') as f2:
            output = json.load(f2)
            if fast_sanity_check:
                with open(output_file_check, 'r') as f3:
                    check = json.load(f3)
                    if output and not io_check(check, output):
                        raise IOGenerationError
            io_pairs.append({'input': json.load(f1), 'output': output})
    return io_pairs, iospec, wrapper


def run_io(ground_truth_io_pairs, compiled_wrapper_path):
    output_io_pairs = []
    for io_pair in ground_truth_io_pairs:
        with get_tmp_path(content=None, suffix='.json') as input_tmp_json_path:
            output_file = ''.join(input_tmp_json_path.split(".")[:1]) + '-out.json'
            with open(input_tmp_json_path, 'w') as f:
                json.dump(io_pair['input'], f)
            stdout, stderr = run_command(f'{compiled_wrapper_path} {input_tmp_json_path} {output_file}')
        with open(output_file, 'r') as f:
            output_io_pairs.append({'input': io_pair['input'], 'output': json.load(f)})
    return output_io_pairs


class ExeError(Exception):
    pass


class ExeBenchFunc:
    def __init__(self, deps, assem, ):
        # self._row = exebench_row
        self._compiled_real = self._compile_real()
        self._compiled_synth = self._compile_synth()

    @classmethod
    def from_exebench_row(cls, exebench_row):
        return cls()

    @classmethod
    def f

    def run_real_io(self, inp):
        assert self._compiled_real
        return self(inp, executable=self._compiled_real)

    def run_synth_io(self, inp):
        assert self._compiled_synth
        return self(inp, executable=self._compiled_synth)

    def run_real_all_io_in_row(self):
        assert self._compiled_real
        outputs = []
        for inp in self._row('')
            return self(inp, executable=self._compiled_real)

    def __call__(self, inp, executable):
        with get_tmp_path(content=None, suffix='.json') as input_tmp_json_path:
            output_file = ''.join(input_tmp_json_path.split(".")[:1]) + '-out.json'
            with open(input_tmp_json_path, 'w') as f:
                json.dump(inp, f)
            stdout, stderr = run_command(f'{executable} {input_tmp_json_path} {output_file}')
            with open(output_file, 'r') as f:
                output = json.load(f)

        return output


class Wrapper:
    def __init__(self, deps, assembly, assembler):
        self._compiled_exe_path = self._compile_exe_path(deps, assembly, assembler)

    @staticmethod
    def _compile_exe_path(deps, assembly, assembler):
        return ''

    def __call__(self, inp):
        executable = self._compiled_exe_path
        with get_tmp_path(content=None, suffix='.json') as input_tmp_json_path:
            output_file = ''.join(input_tmp_json_path.split(".")[:1]) + '-out.json'
            with open(input_tmp_json_path, 'w') as f:
                json.dump(inp, f)
            stdout, stderr = run_command(f'{executable} {input_tmp_json_path} {output_file}')

            with open(output_file, 'r') as f:
                output = json.load(f)

        return output


class ExeBenchRowWrapper:
    def __init__(self, exebench_row):
        self._synth_wrapper = W
        # self._row = exebench_row
        self._compiled_real = self._compile_real()
        self._compiled_synth = self._compile_synth()

    @classmethod
    def from_exebench_row(cls, exebench_row):
        return cls()

    @classmethod
    def f

    def run_real_io(self, inp):
        assert self._compiled_real
        return self(inp, executable=self._compiled_real)

    def run_synth_io(self, inp):
        assert self._compiled_synth
        return self(inp, executable=self._compiled_synth)

    def run_real_all_io_in_row(self):
        assert self._compiled_real
        outputs = []
        for inp in self._row('')
            return self(inp, executable=self._compiled_real)

    def __call__(self, inp, executable):
        with get_tmp_path(content=None, suffix='.json') as input_tmp_json_path:
            output_file = ''.join(input_tmp_json_path.split(".")[:1]) + '-out.json'
            with open(input_tmp_json_path, 'w') as f:
                json.dump(inp, f)
            stdout, stderr = run_command(f'{executable} {input_tmp_json_path} {output_file}')
            with open(output_file, 'r') as f:
                output = json.load(f)

        return output


def diff_io(observed_output, expected_output) -> bool:
    if type(observed_output) is not type(expected_output):
        return False
    if isinstance(observed_output, list):
        if len(observed_output) != len(expected_output):
            return False
        for e1, e2 in zip(observed_output, expected_output):
            ok = diff_io(e1, e2)
            if not ok:
                return False
    elif isinstance(observed_output, dict):
        for key in observed_output:
            if key not in expected_output:
                return False
            ok = diff_io(observed_output[key], expected_output[key])
            if not ok:
                return False
    elif isinstance(observed_output, float):
        ok = math.isclose(observed_output, expected_output)
        if not ok:
            return False
    else:
        ok = observed_output == expected_output
        if not ok:
            return False
    return True
