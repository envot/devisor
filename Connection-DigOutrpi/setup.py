import setuptools

setuptools.setup(
    name="connection-digoutrpi",
    version="0.0.2",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A class to providing a digout connection for Raspberry Pi GPIO.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
