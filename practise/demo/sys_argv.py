

# Test sys.argv

import sys
import os

if __name__ == "__main__":
  arg0 = sys.argv[0]
  print(arg0)
  sys.exit(2)
  