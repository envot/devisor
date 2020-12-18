import setuptools

setuptools.setup(
    name="device-tektronixds2004c",
    version="0.1.1",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device to handle Tektronix DS2004C oscilloscope.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
