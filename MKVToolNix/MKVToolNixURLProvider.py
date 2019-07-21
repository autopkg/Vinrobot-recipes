#!/usr/bin/python

import re, urllib2, urlparse

from HTMLParser import HTMLParser
from distutils.version import StrictVersion
from autopkglib import Processor, ProcessorError

__all__ = [ "MKVToolNixURLProvider" ]

class URLFinder(HTMLParser):
	urls = []

	def handle_starttag(self, tag, attrs):
		if tag == "a":
			for key, value in attrs:
				if key == "href":
					self.urls.append(value)
					break

	@staticmethod
	def get_all_urls_for_url(url):
		content = urllib2.urlopen(url).read()
		parser = URLFinder()
		parser.feed(content)
		return parser.urls


class MKVToolNixURLProvider(Processor):
	"""Provides a version number and dmg download url for MKVToolNix."""
	description = __doc__

	source_url = "https://mkvtoolnix.download/macos/"
	url_pattern = "/macos/MKVToolNix-([0-9.]+).dmg"

	input_variables = {
		"source_url": {
			"required": False,
			"description":
				"URL that will be parsed for the final download URL."
				"Default value is 'https://mkvtoolnix.download/macos/'"
		},
		"url_pattern": {
			"required": False,
			"description":
				"Regex pattern that will applied to all URLs found on the"
				"download page. Extracted version number will be evaluated"
				"by distutils StrictVersion."
				"Default value is '/macos/MKVToolNix-([0-9.]+).dmg'"
		},
	}

	output_variables = {
		"version": {
			"description": "Selected Version.",
		},
		"url": {
			"description": "Download URL.",
		},
	}


	def get_download_urls_per_version(self):
		try:
			urls = URLFinder.get_all_urls_for_url(self.source_url)
			url_pattern = re.compile(self.url_pattern)

			download_urls = {}
			for url in urls:
				m = url_pattern.search(url)
				if not (m is None):
					version = m.group(1)
					download_urls[version] = url

			return download_urls
		except urllib2.HTTPError, ValueError:
			raise ProcessorError("Could not parse downloads metadata.")

	def get_highest_version(self, versions):
		versions = map(lambda x: (x, StrictVersion(x)), versions)

		has_changed = True
		selected = versions[0]
		while has_changed:
			has_changed = False
			for version in versions:
				if selected[1] < version[1]:
					has_changed = True
					selected = version

		return selected[0]

	def main(self):
		if 'source_url' in self.env:
			self.source_url = self.env['source_url']
		if 'url_pattern' in self.env:
			self.url_pattern = self.env['url_pattern']

		try:
			download_urls = self.get_download_urls_per_version()
			latest_version = self.get_highest_version(download_urls.keys())
			latest_version_url = download_urls[latest_version]

			self.output("Found download URL for {}: {}".format(latest_version, latest_version_url))

			self.env["version"] = latest_version
			self.env["url"] = urlparse.urljoin(self.source_url, latest_version_url)
		except BaseException as e:
			raise ProcessorError("Could not get a download URL: {}".format(e))


if __name__ == "__main__":
	PROCESSOR = MKVToolNixURLProvider()
	PROCESSOR.execute_shell()
