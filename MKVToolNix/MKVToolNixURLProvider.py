#!/usr/local/autopkg/python


import re
from typing import Iterable

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

    source_url = "https://mkvtoolnix.download/macos/releases/"
    url_pattern = "^/macos/releases/([0-9.]+)/$"
    file_pattern = "^/macos/releases/([0-9.]+)/MKVToolNix-([0-9.-]+)(-universal)?.dmg$"

    input_variables = {
        "source_url": {
            "required": False,
            "description": "URL that will be parsed for the final download URL."
            f"Default value is '{source_url}'",
        },
        "url_pattern": {
            "required": False,
            "description": "Regex pattern that will applied to all URLs found on the release page."
            "Extracted version number will be evaluated by APLooseVersion."
            f"Default value is '{url_pattern}'",
        },
        "file_pattern": {
            "required": False,
            "description": "Regex pattern that will applied to all URLs found on the download page."
            f"Default value is '{file_pattern}'",
        },
    }

    output_variables = {
        "version": {"description": "Selected Version."},
        "url": {"description": "Download URL."},
    }

    def get_all_versions(self) -> dict[str, str]:
        try:
            content = self.download(self.source_url, text=True)
            urls = URLFinder.find_urls(content)
            url_pattern = re.compile(self.url_pattern)

            return {
                match.group(1): url for url in urls if (match := url_pattern.match(url))
            }

        except HTTPError as e:
            raise ProcessorError("Could not parse downloads metadata.") from e

    def get_highest_version(self, versions: Iterable[str]) -> str:
        return max(versions, key=APLooseVersion)

    def get_download_urls(self, release_path: str) -> set[str]:
        release_path = urljoin(self.source_url, release_path)

        try:
            content = self.download(release_path, text=True)
            urls = URLFinder.find_urls(content)
            file_pattern = re.compile(self.file_pattern)

            return {url for url in urls if file_pattern.match(url)}

        except HTTPError as e:
            raise ProcessorError("Could not parse downloads metadata.") from e

    def get_download_url(self, release_path: str) -> str:
        urls = self.get_download_urls(release_path)

        if len(urls) > 1:
            raise ProcessorError(f"Multiple download URLs found: {', '.join(urls)}")

        return next(iter(urls))

    def main(self):
        if "source_url" in self.env:
            self.source_url = self.env["source_url"]
        if "url_pattern" in self.env:
            self.url_pattern = self.env["url_pattern"]

        try:
            all_versions = self.get_all_versions()
            latest_version = self.get_highest_version(all_versions.keys())
            latest_version_url = self.get_download_url(all_versions[latest_version])

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
