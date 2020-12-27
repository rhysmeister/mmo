import setuptools


with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='mongodbmanager',
    version='0.1.1',
    scripts=['mm'] ,
    author="Rhys Campbell",
    author_email="rhys.james.campbell@googlemail.com",
    description="A simple utility for managing MongoDB Sharded Clusters",
    long_description=open("../README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rhysmeister/mmo",
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
    py_modules=[
        'pymmo',
        'bgcolours',
        'CSVWriter'
    ],
    install_requires=[
        'pymongo',
        'argparse'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
 )
