from setuptools import setup, find_packages
setup(
    name="snapper_systemd_boot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "reprutils",
    ],
    extras_require={
        "dev": ["pytest"],
    },
)
