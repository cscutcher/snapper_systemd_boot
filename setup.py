from setuptools import setup, find_packages
setup(
    name="snapper_systemd_boot",
    description="Generate systemd-boot entries from snapper btrfs snapshots.",
    version="0.1.0-prealpha",
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
    },
    python_requires=">=3.6",
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Systems Administration",
    ],
    keywords="systemd-boot snapper btrfs",
)
