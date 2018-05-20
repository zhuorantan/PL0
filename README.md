# PL/0
### A PL/0 programming language compiler implemented with Python 3 and LLVM

# Usage
```shell
python main.py path/to/pl0/source/file
```

# Requirements
This program generates LLVM IR code. In order to generate executable binaries, LLVM command line tool and GCC have to be installed.

On macOS, LLVM can be installed via
```shell
brew install llvm
```
Since homebrew doesn't symlink LLVM into /usr/local, you have to manually add the path of `llc` to `PATH` environment variable, or provide the path of `llc` by
```shell
python main.py path/to/pl0/source/file -llc /usr/local/opt/llvm/bin/llc
```

# [License](LICENSE)
