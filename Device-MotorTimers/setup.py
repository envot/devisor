import setuptools

setuptools.setup(
    name="device-motortimers",
    version="0.1.0",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device to handle motors (two directions) with timers.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
