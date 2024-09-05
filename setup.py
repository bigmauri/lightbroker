import setuptools

with open("README.md", "r", encoding="utf-8") as _f:
    long_description = _f.read()

setuptools.setup(
    name="light-broker-bigmauri",
    version="0.0.1",
    author="Maurizio Bussi",
    author_email="maurizio.bussi.mb@gmail.com",
    description="Broker package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bigmauri/light-broker",
    project_urls={
        "Bug Tracker": "https://github.com/bigmauri/light-broker/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
)