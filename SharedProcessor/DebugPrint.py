#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

from autopkglib import Processor, ProcessorError

__all__ = ["DebugPrint"]


class DebugPrint(Processor):
    """Print a variable in console.

    Useful to debug.
    """

    description = __doc__

    input_variables = {
        "variable_name": {
            "required": True,
            "description": "The name of the variable to print.",
        }
    }

    output_variables = {}

    def main(self):
        variable_name = self.env["variable_name"]
        if variable_name == "*":
            print(self.env)
        else:
            print(self.env[variable_name])


if __name__ == "__main__":
    PROCESSOR = DebugPrint()
    PROCESSOR.execute_shell()
