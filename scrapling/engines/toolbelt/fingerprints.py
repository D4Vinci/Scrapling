"""
Functions related to generating headers and fingerprints generally
"""

import platform

from tldextract import extract
from browserforge.fingerprints import FingerprintGenerator
from browserforge.headers import HeaderGenerator, Browser


def generate_convincing_referer(url):
    """
    Takes the domain from the URL without the subdomain/suffix and make it look like you were searching google for this website

    >>> generate_convincing_referer('https://www.somewebsite.com/blah')
    'https://www.google.com/search?q=somewebsite'

    :param url: The URL you are about to fetch.
    :return:
    """
    website_name = extract(url).domain
    return f'https://www.google.com/search?q={website_name}'


def get_os_name():
    # Get the OS name in the same format needed for browserforge
    os_name = platform.system()
    return {
        'Linux': 'linux',
        'Darwin': 'macos',
        'Windows': 'windows',
        # For the future? because why not
        'iOS': 'ios',
    }.get(os_name)


def generate_suitable_fingerprint():
    # This would be for Browserforge playwright injector
    os_name = get_os_name()
    return FingerprintGenerator(
        browser=[Browser(name='chrome', min_version=128)],
        os=os_name,  # None is ignored
        device='desktop'
    ).generate()


def generate_headers(browser_mode=False):
    if browser_mode:
        # In this mode we don't care about anything other than matching the OS and the browser type with the browser we are using
        # So we don't raise any inconsistency red flags while websites fingerprinting us
        os_name = get_os_name()
        return HeaderGenerator(
            browser=[Browser(name='chrome', min_version=128)],
            os=os_name,  # None is ignored
            device='desktop'
        ).generate()
    else:
        # Here it's used for normal requests that aren't done through browsers so we can take it lightly
        browsers = [
            Browser(name='chrome', min_version=120),
            Browser(name='firefox', min_version=120),
            Browser(name='edge', min_version=120),
        ]
        return HeaderGenerator(browser=browsers, device='desktop').generate()
