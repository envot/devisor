import setuptools

setuptools.setup(
    name="device-rgamks113",
    version="0.1.1",
    author="Ceki99",
    author_email="antonio.cerovic@gmail.com",
    description="A device to handle Residual Gas Analyzer MKS113.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
