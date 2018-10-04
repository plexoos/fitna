import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "fitna",
    version = "0.0.2",
    author = "Dmitri Smirnov",
    author_email = "dmixsmi@gmail.com",
    description = "Data fitting algorithms",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/plexoos/toufy",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering"
    ],
)
