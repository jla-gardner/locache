import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="locache",
    version="2.0.1",
    description="Cache expensive function calls to disk.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jla-gardner/local-cache",
    author="John Gardner",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["locache"],
    keywords=["cache"],
    install_requires=[],
    package_data={},
    python_requires=">=3.7, <4",
)
