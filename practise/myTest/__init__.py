import sys

def main():
    try:
        # Your code here
        print("This is a message to stdout.")
        raise ValueError("This is a test error.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()