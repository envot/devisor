import setuptools

setuptools.setup(
    name="device-artiqkasli",
    version="0.0.1",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device to handle ARTIQ Kasli of Sinara hardware.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
