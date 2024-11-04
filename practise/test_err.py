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


{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Gunicorn",
            "type": "python",
            "request": "launch",
            "module": "gunicorn",
            "args": [
                "--reload",
                "--workers",
                "3",
                "--bind",
                "127.0.0.1:5000",
                "your_app_module:app"
            ],
            "console": "integratedTerminal"
        }
    ]
}