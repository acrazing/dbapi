#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 acrazing <joking.young@gmail.com>. All rights reserved.
# @since 2018-07-10 15:38:36
import inspect
import json
import sys

from dbapi.DoubanAPI import DoubanAPI
from dbapi.base import ModuleAPI


def format_func(fn):
    args = inspect.getfullargspec(fn)
    if args.args[0] == "self":
        args.args.pop(0)
    options = "<" + "> <".join(args.args) + ">" if len(args.args) > 0 else ""
    if args.varargs is not None:
        options += " <" + args.varargs + ">"
    if args.varkw is not None:
        options += " <" + args.varkw + ">"
    return options[1:] if options.startswith(" ") else options


def default(data):
    try:
        return data.toJSON()
    except:
        try:
            return data.__repr__()
        except:
            try:
                return data.__class__.__name__
            except:
                return '__UNKNOWN__'


def show_help(api, error):
    lines = []
    if error is not None:
        lines.append("ERROR: " + error + "\n")
    lines.append("Usage:")
    lines.append("    " + sys.argv[0] + " <api> [options...]")
    lines.append("    " + sys.argv[0] + " <module> <api> [options...]\n")
    lines.append("Available API:")

    for k in sorted(dir(api), key=lambda x: (isinstance(getattr(api, x), ModuleAPI), x)):
        if k.startswith("_"):
            continue
        attr = getattr(api, k, None)
        if callable(attr):
            lines.append(" - " + k + " " + format_func(attr))
        elif isinstance(attr, ModuleAPI):
            lines.append(" - " + k)
            for k1 in dir(attr):
                if k1.startswith("_"):
                    continue
                attr1 = getattr(attr, k1, None)
                if callable(attr1):
                    lines.append("    - " + k + " " + k1 + " " + format_func(attr1))
    print("\n".join(lines))
    if error is not None:
        sys.exit(1)


def main():
    api = DoubanAPI()
    if len(sys.argv) < 2 or sys.argv.count("--help") > 0 or sys.argv.count("-h") > 0:
        show_help(api, None)
        return
    method = getattr(api, sys.argv[1])
    args = sys.argv[2:]
    if isinstance(method, ModuleAPI):
        if len(sys.argv) < 3:
            show_help(api, "Please specify the API")
            return
        method = getattr(method, sys.argv[2])
        args = sys.argv[3:]
    if not callable(method):
        show_help(api, "Specified API is not a valid function")
        return
    print(json.dumps(method(*args), indent=2, default=default))


if __name__ == "__main__":
    main()
