import setuptools

setuptools.setup(
    name="connection-pca9685",
    version="0.1.0",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A class to providing a pca9685 connection over an i2cbus.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
