__trace_stack = []
__trace_stack_reversed = []


def traced(func, max_args=2, indent=2):
    """Decorator to trace function calls"""

    def wrapper(*args):
        global __trace_stack
        global __trace_stack_reversed
        try:
            name = args[0].objectName()
            name += "."
            selection = slice(1, 1 + max_args)
        except Exception as e:
            name = ""
            selection = slice(0, max_args)
        args_str = ", ".join([str(arg) for arg in args[selection]])
        __trace_stack.append(f"{name}{func.__name__}({args_str}) -> ")

        result = func(*args)

        __trace_stack_reversed.append(__trace_stack.pop(-1) + f"{result}")
        if not __trace_stack:
            for depth, txt in enumerate(reversed(__trace_stack_reversed)):
                print(" " * indent * depth, txt, sep="")
            __trace_stack_reversed.clear()
        return result

    return wrapper
