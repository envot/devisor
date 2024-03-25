import setuptools

setuptools.setup(
    name="connection-telnet",
    version="0.1.2",
    author="schueppi, Jakob, Ceki99",
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
