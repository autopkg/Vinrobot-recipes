#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import re

from autopkglib import Processor, ProcessorError

__all__ = [ "RegexReplace" ]

class RegexReplace(Processor):
	"""Replaces sequence of the input that matches the pattern with the given
	replacement string.

	If the pattern isn't found, string is returned unchanged.
	https://docs.python.org/2/library/re.html#re.sub
	"""
	description = __doc__

	input_variables = {
		"result_output_var_name": {
			"required": True,
			"description":
				"The name of the output variable that is returned by the replacement."
		},
		"re_string": {
			"required": True,
			"description":
				"The sequence to "
		},
		"re_pattern": {
			"required": True,
			"description":
				"Regular expression (Python) to match against page.",
		},
		"re_replacement": {
			"required": True,
			"description": "Replacement for the rege",
		},
		"re_flags": {
			"required": False,
			"description":
				"Optional array of strings of Python regular expression "
				"flags. E.g. IGNORECASE."
		}
	}

	output_variables = {
		"result_output_var_name": {
			"description":
				"First matched sub-pattern from 're_string'. Note the actual name "
				"of variable depends on the input variable 'result_output_var_name'"
		}
	}

	def replace(self, pattern, replacement, string, flags):
		# https://github.com/autopkg/autopkg/blob/master/Code/autopkglib/URLTextSearcher.py#L91
		flag_accumulator = 0
		if flags:
			for flag in flags:
				if flag in re.__dict__:
					flag_accumulator += re.__dict__[flag]

		return re.sub(pattern, replacement, string, flags=flag_accumulator)

	def main(self):
		output_var_name = self.env['result_output_var_name']

		re_string = self.env['re_string']
		re_replacement = self.env['re_replacement']

		re_pattern = self.env['re_pattern']
		re_flags = self.env['re_flags']

		result = self.replace(re_pattern, re_replacement, re_string, re_flags)

		self.env[output_var_name] = result


if __name__ == "__main__":
	PROCESSOR = RegexReplace()
	PROCESSOR.execute_shell()
