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



# Paths to emit output to.
ROOT=os.path.dirname(os.path.realpath(__file__))
OPAMROOT=os.path.join(ROOT, '_opam')
RESULT=os.path.join(ROOT, '_result')
SIZE_PATH = os.path.join(RESULT, 'size.json')
MACRO_PATH = os.path.join(RESULT, 'macro.json')
MICRO_PATH = os.path.join(RESULT, 'micro.json')
PERF_PATH = os.path.join(RESULT, 'perf')
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
      choices=[n for n in dir(macro) if not n.startswith('__') and n != 'Macro'],
      help='macro benchmark to run'
  )
  parser.add_argument(
      '-micro',
      type=str,
      action='store',
      default=None,
      choices=[n for n in dir(micro) if not n.startswith('__') and n != 'Micro'],
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
  parser.add_argument('-time-build', default=False, action='store_true')
  args = parser.parse_args()

  # Raise stack limit to 128Mb.
  stack_size = 128 * 1024 * 1024
  resource.setrlimit(resource.RLIMIT_STACK, (stack_size, stack_size))

  # Build and run.
  switches = args.switches.split(',')
  if args.build:
    build.install(switches, args.repository, args.jb, args.test)
  if args.size:
    size.benchmark_size(switches, OPAMROOT, SIZE_PATH)
  if args.macro and not args.perf:
    tests = getattr(macro, args.macro)
    run.benchmark_macro(tests, switches, args.n, args.jt, ROOT, MACRO_PATH)
  if args.macro and args.perf:
    tests = getattr(macro, args.macro)
    perf.benchmark_macro(tests, switches, ROOT, PERF_PATH)
  if args.micro:
    tests = getattr(micro, args.micro)
    run.benchmark_micro(tests, switches, MICRO_PATH)
