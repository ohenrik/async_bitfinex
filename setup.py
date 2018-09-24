from setuptools import setup, find_packages

VERSION = '0.8.1'

# Runtime dependencies. See requirements.txt for development dependencies.
DEPENDENCIES = [
    'requests',
    'httpretty',
    "twisted",
    "autobahn",
    "pyopenssl",
    "service_identity",
]

setup(
    name='bitfinex-v2',
    version=VERSION,
    description='Python client for the Bitfinex API',
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
