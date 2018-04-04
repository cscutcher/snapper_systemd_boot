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
    """
    Config with sensible values and mock files to represent the real thing.

    As with most of this app, currently this is all heavily based on my
    particular setup.
    """
    fake_root = Path(tmpdir.mkdir("fake_root"))
    boot_path = fake_root / "boot"
    boot_path.mkdir()

    systemd_entries_path = boot_path / "loader/entries"
    systemd_entries_path.mkdir(parents=True)

    image_source_dir = fake_root / ".bootbackup"
    image_source_dir.mkdir()

    kernel_image_source = image_source_dir / "vmlinuz-linux"
    kernel_image_source.touch()

    initramfs_image_source = image_source_dir / "initramfs-linux.img"
    initramfs_image_source.touch()

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
        entry_template=entry_template,
        kernel_image_source=kernel_image_source.relative_to(fake_root),
        initramfs_image_source=initramfs_image_source.relative_to(fake_root),
        images_snapshot_dir="snapper",
        boot_path=boot_path,
        root_subvolume="@",
    )

    for f in systemd_entries_path.iterdir():
        print(f)
        print(f.open("r").read())
