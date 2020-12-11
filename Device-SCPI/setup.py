import setuptools

setuptools.setup(
    name="device-scpi",
    version="0.1.0",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device to handle generic SCPI devices mostly used as a parent class for other SCPI devices.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
