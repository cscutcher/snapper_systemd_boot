from pathlib import Path
from textwrap import dedent

import pytest

from snapper_systemd_boot.config import SnapperSystemDBootConfig
from snapper_systemd_boot import context


@pytest.fixture(scope="session")
def snapper():
    return context.get_snapper()


@pytest.fixture
def config(tmpdir):
    systemd_entries_path = Path(tmpdir.mkdir("systemd_entries"))

    entry_template = dedent("""
        title Arch Linux (Snapshot {snapshot.iso_timestamp} [{snapshot.num}])
        linux /vmlinuz-linux
        initrd /initramfs-linux.img
        options \
            cryptdevice=UUID=d79c85d5-0ed6-4b92-b3dd-e7b6fc7dee9f:aeryn-root-crypt\
            root=/dev/mapper/aeryn-root-crypt quiet rw\
            rootflags=subvol=@/.snapshots/{snapshot.num}/snapshot
    """)

    yield SnapperSystemDBootConfig(
        systemd_entries_path=systemd_entries_path,
        entry_prefix="arch-auto-snapshot-",
        entry_template=entry_template)

    for f in systemd_entries_path.iterdir():
        print(f)
        print(f.open("r").read())
