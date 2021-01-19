from setuptools import setup

setup(
    name="philsite",
    packages=["philsite"],
    include_package_data=True,
    install_requires=[
        "flask",
        "numpy",
        "matplotlib",
    ],
)
