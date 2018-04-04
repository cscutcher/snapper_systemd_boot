from setuptools import setup, find_packages
setup(
    name="snapper_systemd_boot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "reprutils",
        "argh",
        "sh",
    ],
    extras_require={
        "dev": ["pytest"],
    },
    entry_points={
        "console_scripts": [
            "snapper-systemd-boot = snapper_systemd_boot.cli:main",
        ]
    }
)
