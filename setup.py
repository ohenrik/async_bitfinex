from setuptools import setup, find_packages

VERSION = '0.4.1'

# Runtime dependencies. See requirements.txt for development dependencies.
DEPENDENCIES = [
    'requests',
    'httpretty',
    "twisted",
    "autobahn",
    "pyopenssl",
    "service_identity",
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='bitfinex-v2',
    version=VERSION,
    description='Python client for the Bitfinex API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Ole Henrik Skogstrøm',
    author_email='henrik@amplify.no',
    url='https://github.com/ohenrik/bitfinex',
    license='MIT',
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    # download_url='https://github.com/ohenrik/bitfinex/tarball/%s' % version,
    keywords=['bitcoin', 'btc'],
    classifiers=[],
    zip_safe=True
)
