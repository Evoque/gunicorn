

import sys
import socketserver

def method1():
    print("in method1")
    sys.exit(0)

def main():
    print("in Main ")
    print("before invoke method1")
    method1()
    print("after invoke method1")
    
main()
    