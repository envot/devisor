import setuptools

setuptools.setup(
    name="device-nextbike",
    version="0.0.1",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device to collect station info from nextbike.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
