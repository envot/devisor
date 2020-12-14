import setuptools

setuptools.setup(
    name="device-rigoltechnologiesdg2102",
    version="0.1.1",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device to handle a Rigol Technologies DG 2102 frequency generator.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
