import setuptools

setuptools.setup(
    name="device-bridge",
    version="0.1.0",
    author="Ceki99, schueppi",
    author_email="antonio.cerovic@gmail.com, schueppi@schueppi.com",
    description="A device to handle Digital Laser Controller device.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
