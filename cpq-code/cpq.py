import sys

sys.path.insert(0, "sly-master\\src\\")
from compiler import Compiler

if __name__ == "__main__":
    cpq_compiler = Compiler()
    cpq_compiler.run_on_file(sys.argv[1])
