import setuptools

setuptools.setup(
    name="connection-digoutmcp23017",
    version="0.1.0",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A class to providing a digout of MCP23017.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
