import argparse

print(argparse.__file__)


# parser = argparse.ArgumentParser()

# print(__file__)

# parser.add_argument("x", type=int, help="the base")
# parser.add_argument("y", type=int, help="the exponent")
# parser.add_argument("-v", "--verbosity", action="count", default=0)
# parser.add_argument("1", nargs="+")

# args = parser.parse_args()
# answer = args.x**args.y

# if args.verbosity >= 2:
#     print(f"{args.x} to the power {args.y} equals {answer}")
# elif args.verbosity >= 1:
#     print(f"{args.x}^{args.y} == {answer}")
# else:
#     print(answer)
