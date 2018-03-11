from setuptools import setup

version = '0.2.6'

# Runtime dependencies. See requirements.txt for development dependencies.
dependencies = [
    'requests',
    'httpretty',
    "twisted",
    "autobahn",
    "pyopenssl",
    "service_identity",
]

setup(name='bitfinex',
    version=version,
    description='Python client for the Bitfinex API',
    author='Ole Henrik Skogstrøm',
    author_email='henrik@amplify.no',
    url='https://github.com/ohenrik/bitfinex',
    license='MIT',
    packages=['bitfinex'],
    install_requires=dependencies,
    # download_url='https://github.com/ohenrik/bitfinex/tarball/%s' % version,
    keywords=['bitcoin', 'btc'],
    classifiers=[],
    zip_safe=True)
