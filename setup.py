import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-gls-connector",
    version="0.1.0",
    author="Viliam Tokarcik",
    author_email="viliam@tokarcik.eu",
    description="Python library for using GLS Online API for printing labels",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pipoline/python-gls-connector",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)