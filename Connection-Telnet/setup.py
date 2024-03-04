import setuptools

setuptools.setup(
    name="connection-scpi",
    version="0.1.0",
    author="schueppi, Jakob",
    author_email="schueppi@schueppi.com",
    description="A class to providing a Telnet connection.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
