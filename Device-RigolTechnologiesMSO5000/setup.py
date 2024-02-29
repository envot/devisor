import setuptools

setuptools.setup(
    name="device-rigoltechnologiesmso5000",
    version="0.1.0",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device to handle a Rigol Technologies MSO 5000 osciloscope.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
