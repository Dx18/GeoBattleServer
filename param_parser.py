#import simple_test

def parse_params(params):
    result = dict()

    index = 0
    while index < len(params):
        if params[index].startswith("-"):
            if index < len(params) - 1 and not params[index + 1].startswith("-"):
                result[params[index]] = params[index + 1]
                index += 2
            else:
                result[params[index]] = None
                index += 1
        else:
            raise ValueError("Cannot parse parameters: unexpected value '{}'".format(params[index]))

    return result

if __name__ == "__main__":
    simple_test.test_eq(
        "1",
        parse_params(["-a", "5", "-b", "c", "-d", "-e", "-f"]),
        { "-a": "5", "-b": "c", "-d": None, "-e": None, "-f": None }
    )

    simple_test.test_eq(
        "2",
        parse_params(["-a", "5", "-b", "c", "-d", "-e", "f"]),
        { "-a": "5", "-b": "c", "-d": None, "-e": "f" }
    )

    simple_test.test_eq(
        "3",
        parse_params(["-a"]),
        { "-a": None }
    )

    simple_test.test_err(
        "4",
        lambda: parse_params(["a"]),
        ValueError
    )

    simple_test.test_err(
        "5",
        lambda: parse_params(["-a", "a", "a"]),
        ValueError
    )
