import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="librus_tricks",
    version="0.0.1",
    author="Krystian Postek",
    author_email="krystian@postek.eu",
    description="A python wrapper of Synergia Librus API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Backdoorek/LibrusTricks",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)