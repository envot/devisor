import setuptools

setuptools.setup(
    name="connection-pwmpca9685",
    version="0.0.1",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A class to providing a single pwm channel of a pca9685.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)