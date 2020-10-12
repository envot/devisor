import setuptools

setuptools.setup(
    name="connection-pwmrpi",
    version="0.0.1",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A class to providing a pwm connection for Raspberry Pi GPIO (untested).",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
