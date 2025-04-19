from setuptools import find_packages, setup

setup(
    name="ds",
    version="0.1.0",
    description="Minimum code to implement Deep deep using deepseek LLM",
    author="Ranch Lai",
    author_email="ranchlai@163.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        # Add other dependencies your package needs
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache License 2.0",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
