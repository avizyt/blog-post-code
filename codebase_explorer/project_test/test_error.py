def divide_numbers():
    try:
        result = 10 / 0
    except Exception as e:
        import traceback

        with open("error_trace.txt", "w") as f:
            f.write(traceback.format_exc())
        raise e


if __name__ == "__main__":
    divide_numbers()
