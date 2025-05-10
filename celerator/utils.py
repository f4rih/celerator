import ast


def convert_args_safely(r: str | None, k: str | None):
    args = None
    kwargs = None
    if r:
        args = ast.literal_eval(f"({r},)" if ',' not in r else f"({r})")
    if k:
        fake_call = f"f({k})"
        parsed = ast.parse(fake_call, mode='eval')
        kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in parsed.body.keywords}

    return args, kwargs
