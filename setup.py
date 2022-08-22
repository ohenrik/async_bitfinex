from setuptools import find_packages, setup

VERSION = '0.4.2'

# Runtime dependencies. See requirements.txt for development dependencies.
DEPENDENCIES = [
    'requests',
    "websockets",
]

def get_readme(readme_location="README.md"):
    with open(readme_location, "r", "utf-8") as f:
        readme = f.read()
    return readme

setup(
    name='async_bitfinex',
    version=VERSION,
    description='Python client for Bitfinex ',
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    author='Ole Henrik Skogstrøm',
    author_email='henrik@amplify.no',
    url='https://github.com/ohenrik/async_bitfinex',
    project_urls = {
        "Documentation": "https://async_bitfinex.readthedocs.io/en/latest/",
        "Source": "https://github.com/ohenrik/async_bitfinex"
    }
    license='MIT',
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    # download_url='https://github.com/ohenrik/bitfinex/tarball/%s' % version,
    keywords=['bitfinex', 'bitcoin', 'btc', 'asyncio', 'websockets']
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Intended Audience :: Financial and Insurance Industry",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7"
    ],
    zip_safe=True
)
