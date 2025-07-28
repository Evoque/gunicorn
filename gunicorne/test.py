import sys
import time

print("hello")
a = 100
print("\nError: %s" % str(a), file=sys.stderr)

time.sleep(10)