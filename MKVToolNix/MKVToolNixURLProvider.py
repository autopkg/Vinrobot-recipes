#!/usr/local/autopkg/python


import re

from autopkglib import APLooseVersion, ProcessorError, URLGetter

try:
    from html.parser import HTMLParser
    from urllib.error import HTTPError
    from urllib.parse import urljoin  # For Python 3
except ImportError:
    from HTMLParser import HTMLParser
    from urllib2 import HTTPError
    from urlparse import urljoin  # For Python 2

__all__ = ["MKVToolNixURLProvider"]


class URLFinder(HTMLParser):
    urls = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for key, value in attrs:
                if key == "href":
                    self.urls.append(value)
                    break

    @staticmethod
    def find_urls(content):
        parser = URLFinder()
        parser.feed(content)
        return parser.urls


class MKVToolNixURLProvider(URLGetter):
    """Provides a version number and dmg download url for MKVToolNix."""

    description = __doc__

    source_url = "https://mkvtoolnix.download/macos/"
    url_pattern = "/macos/MKVToolNix-([0-9.]+).dmg"

    input_variables = {
        "source_url": {
            "required": False,
            "description": "URL that will be parsed for the final download URL."
            "Default value is 'https://mkvtoolnix.download/macos/'",
        },
        "url_pattern": {
            "required": False,
            "description": "Regex pattern that will applied to all URLs found on the"
            "download page. Extracted version number will be evaluated"
            "by APLooseVersion."
            "Default value is '/macos/MKVToolNix-([0-9.]+).dmg'",
        },
    }

    output_variables = {
        "version": {"description": "Selected Version."},
        "url": {"description": "Download URL."},
    }

    def get_download_urls_per_version(self):
        try:
            content = self.download(self.source_url, text=True)
            urls = URLFinder.find_urls(content)
            url_pattern = re.compile(self.url_pattern)

            download_urls = {}
            for url in urls:
                m = url_pattern.search(url)
                if m:
                    version = m.group(1)
                    download_urls[version] = url

            return download_urls
        except HTTPError as e:
            raise ProcessorError("Could not parse downloads metadata.") from e

    def get_highest_version(self, versions):
        return max(versions, key=APLooseVersion)

    def main(self):
        if "source_url" in self.env:
            self.source_url = self.env["source_url"]
        if "url_pattern" in self.env:
            self.url_pattern = self.env["url_pattern"]

        try:
            download_urls = self.get_download_urls_per_version()
            latest_version = self.get_highest_version(download_urls.keys())
            latest_version_url = download_urls[latest_version]

            self.output(
                f"Found download URL for {latest_version}: {latest_version_url}"
            )

            self.env["version"] = latest_version
            self.env["url"] = urljoin(self.source_url, latest_version_url)
        except BaseException as e:
            raise ProcessorError(f"Could not get a download URL: {e}") from e


if __name__ == "__main__":
    PROCESSOR = MKVToolNixURLProvider()
    PROCESSOR.execute_shell()
