import setuptools

setuptools.setup(
    name="device-testdevice",
    version="0.0.2",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device for testing devisor's features.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)