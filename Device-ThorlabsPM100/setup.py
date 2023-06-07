import setuptools

setuptools.setup(
    name="device-thorlabspm100",
    version="0.1.0",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device to handle powermeter PM100(D) from Thorlabs and provide automated power measurements with multiple wavelengths.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
