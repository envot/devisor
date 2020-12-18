import setuptools

setuptools.setup(
    name="connection-usbtmc",
    version="0.2.0",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A class to providing a USBtmc connection.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
