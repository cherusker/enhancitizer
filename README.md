# Enhancitizer (Beta)
**Enhance the reports of various Clang sanitizers.**

- [What It Is](#what-it-is)
- [How To Use It](#how-to-use-it)
- [What It Does](#what-it-does)
- [Technical Stuff](#technical-stuff)

## What It Is

> Please be aware that this software is at the beginning of its life cycle. It produces meaningful output already, yet, every commit might introduce a breaking change without further notice.

The aim of the Enhancitizer is to support the analysis of large projects where [Clang's sanitizers](https://clang.llvm.org/docs/index.html) produce a vast amount of reports. Whenever a flood of reports can hardly be studied _as is_, feed them to the Enhancitizer and work with the reprocessed, enhanced output.

Currently, this software is tailored while working with Clang's reports of the [Mono runtime](https://github.com/mono/mono).

## How To Use It

Using the Enhancitizer is straight forward: make sure that you have logfiles that contain reports of Clang's sanitizers (the more reports the better). Then run something like:

```
$ python3 enhancitizer /home/root/of/code /home/root/of/output /home/path/of/logfiles
```

Afterwards, go to `/home/root/of/output` and study your program! ;)

Details about the usage can be found in [docs/usage.txt](docs/usage.txt) or by running `$ python3 enhancitizer` (without valid arguments).

## What It Does

Different reports ask for different things. Currently, the Enhancitizer supports the following:

|                       | Basic   | Blacklist | Context | Skeleton | Summary | 
| --------------------- |:-------:|:---------:|:-------:|:--------:|:-------:|
| ASan: Over-/Underflow | planned | planned   | planned | planned  |         |
| TSan: Data Race       | yes     | yes       | yes     | yes      | yes     |
| TSan: Thread Leak     | yes     |           |         |          |         |

ASan: [AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html), TSan: [ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html)

**Basic**: detect unique reports in logfiles and copy them into separate report files  
**Blacklist**: add the functions of the top frames of meaningful stack traces to dedicated blacklists  
**Context**: add source code that is referenced by the top frames of meaningful stack traces into the report files  
**Skeleton**: rebuild a skeleton of the project with all referenced source files and marked reports  
**Summary**: provide meaningful summaries, packed into CSV files

## Technical Stuff

So far, the Enhancitizer is developed on Linux and targets the execution with [Python 3](https://docs.python.org/3/). If it works with any other setup, it is pure luck! ;) However, feel free to to add support for other platforms and/or [Python 2](https://docs.python.org/2/).
