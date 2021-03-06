#!/usr/bin/env -S python3 -B

import argparse
import os
import multiprocessing
import resource

import build
import macro
import micro
import size
import run
import perf
import disasm



# Paths to emit output to.
ROOT=os.path.dirname(os.path.realpath(__file__))
OPAMROOT=os.path.join(ROOT, '_opam')
RESULT=os.path.join(ROOT, '_result')
SIZE_PATH = os.path.join(RESULT, 'size.json')
MACRO_PATH = os.path.join(RESULT, 'macro.json')
MICRO_PATH = os.path.join(RESULT, 'micro.json')
PERF_PATH = os.path.join(RESULT, 'perf')
DISASM_PATH = os.path.join(RESULT, 'disasm')
BUILD_TIME_PATH = os.path.join(RESULT, 'build')

# Path to the default repository.
REPOSITORY='git+https://github.com/nandor/llir-opam-repository'



if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='GenM OCaml benchmark suite')
  parser.add_argument(
      '-n',
      type=int,
      default=1,
      action='store',
      help='number of repetitions for macro tests'
  )
  parser.add_argument(
      '-jb',
      type=int,
      default=max(1, multiprocessing.cpu_count() - 1),
      action='store',
      help='number of threads to build with'
  )
  parser.add_argument(
      '-jt',
      type=int,
      default=1,
      action='store',
      help='number of threads to test with'
  )
  parser.add_argument(
      '-macro',
      type=str,
      action='store',
      default=None,
      help='macro benchmark to run'
  )
  parser.add_argument(
      '-micro',
      type=str,
      action='store',
      default=None,
      help='benchmark to run'
  )
  parser.add_argument(
      '-repository',
      type=str,
      action='store',
      default=REPOSITORY,
      help='path to the LLIR opam repository'
  )
  parser.add_argument(
      '-switches',
      type=str,
      default='ref,llir+O0',
      help='comma-separated list of switches to run (ref, llir, llir+On)'
  )
  parser.add_argument(
      '-no-test',
      action='store_false',
      dest='test',
      help='do not run tests'
  )
  parser.add_argument(
      '-no-size',
      action='store_false',
      dest='size',
      help='do not benchmark size'
  )
  parser.add_argument(
      '-apps',
      action='store_true',
      dest='apps',
      help='install apps',
      default=True
  )
  parser.add_argument(
      '-no-apps',
      action='store_false',
      dest='apps',
      help='do not install apps'
  )
  parser.add_argument(
      '-no-build',
      action='store_false',
      dest='build',
      help='do not build'
  )
  parser.add_argument(
      '-perf',
      action='store_true',
      dest='perf',
      help='find hot methods using perf'
  )
  parser.add_argument(
      '-disasm',
      action='store_true',
      dest='disasm',
      help='disassemble binaries'
  )
  parser.add_argument('-time-build', default=False, action='store_true')
  args = parser.parse_args()

  # Raise stack limit to 128Mb.
  stack_size = 128 * 1024 * 1024
  resource.setrlimit(resource.RLIMIT_STACK, (stack_size, stack_size))

  macro_tests = []
  if args.macro:
    macro_tests = sum([getattr(macro, m) for m in args.macro.split(',')], [])
  micro_tests = []
  if args.micro:
    micro_tests = sum([getattr(micro, m) for m in args.micro.split(',')], [])

  # Build and run.
  switches = args.switches.split(',')
  if args.build:
    build.install(switches, args.repository, args.jb, args.test, args.apps)
  if args.apps and (macro_tests or micro_tests):
    build.build(switches, args.jb, macro_tests, micro_tests)
  if args.apps and args.size:
    size.benchmark_size(switches, OPAMROOT, SIZE_PATH)
  if args.apps and (macro_tests and not args.perf):
    run.benchmark_macro(macro_tests, switches, args.n, args.jt, ROOT, MACRO_PATH)
  if args.apps and (macro_tests and args.perf):
    perf.benchmark_macro(macro_tests, switches, ROOT, PERF_PATH)
  if args.apps and micro_tests:
    run.benchmark_micro(micro_tests, switches, MICRO_PATH)
  if args.apps and args.disasm:
    disasm.benchmark_insts(switches, ROOT, DISASM_PATH)
