from setuptools import setup, find_packages

VERSION = '0.2.0'

# Runtime dependencies. See requirements.txt for development dependencies.
DEPENDENCIES = [
    'requests',
    "websockets",
]

setup(
    name='async_bitfinex',
    version=VERSION,
    description='Python client for Bitfinex ',
    author='Ole Henrik Skogstrøm',
    author_email='henrik@amplify.no',
    url='https://github.com/ohenrik/async_bitfinex',
    license='MIT',
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    # download_url='https://github.com/ohenrik/bitfinex/tarball/%s' % version,
    keywords=['bitfinex', 'bitcoin', 'btc', 'asyncio', 'websockets'],
    classifiers=[],
    zip_safe=True
)
