import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="librus_tricks",
    python_requires='>3.6.0',
    version="0.3.0",
    author="Krystian Postek",
    author_email="krystian@postek.eu",
    description="A python wrapper of Synergia Librus API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Backdoorek/LibrusTricks",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests', 'beautifulsoup4'
    ],
    extras_require={
        'examples': ['colorama', 'matplotlib', 'PrettyTable']
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Polish",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)