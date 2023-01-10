#!/usr/bin/env python3

# import os


def format_parameter(number_str, pad_before=6, pad_after=7):
    try:
        whole, frac = number_str.split(".")
    except ValueError:
        whole = number_str.split(".")[0]
        frac = None
    pad_before_adj = max(pad_before - len(whole), 2)  # Leave two spaces at a minimum
    whole = " " * pad_before_adj + whole
    pad_after_adj = min(pad_after, (pad_after + pad_before - len(whole)))
    if frac is None:
        number_str = whole + " " * (pad_after_adj + 1)
    else:
        frac = "." + frac + " " * (pad_after_adj - len(frac))
        number_str = whole + frac
    return number_str
