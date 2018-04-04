# -*- coding: utf-8 -*-
"""
Main module for managing systemd-boot entries from snapper snapshots.
"""
from pathlib import Path
import logging
import shutil

from distutils.util import strtobool
import pytest
import sh

DEV_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def inst(snapper, config):
    return SnapperSystemDBootManager(snapper, config)


@pytest.mark.real_config
def test_get_root_config(inst):
    """
    Check we can access root snapper config.

    I.e. use the real snapper dbus interface and try and locate the config used
    to back up the root path `/`.
    """
    root_config = inst.get_root_config()
    name, path, config = inst.snapper.snapper.GetConfig(root_config.name)

    assert name == root_config.name
    assert path == str(root_config.path) == "/"


@pytest.mark.real_config
@pytest.mark.dangerous
def test_write_entries(inst):
    """
    Run entry generation and write to disk.

    TODO: This is only barely a test. Actually assert on something!
    """
    inst.write_boot_entries()


@pytest.mark.real_config
def test_generate_entries(inst):
    """
    Test generation of entries.

    TODO: This is only barely a test. Actually assert on something!
    """
    for entry in inst.get_boot_entries():
        print(entry)


class BootEntry:
    """Boot entry generated from snapshot."""

    class EntryTemplateContext:
        def __init__(self, entry, snapshot):
            self.entry = entry
            self.snapshot = snapshot

        @property
        def title_suffix(self):
            MAX_DESCRIPTION_LENGTH = 20
            ELLIPSIS = "..."

            # Frustratingly textwrap.shorten breaks only between wrods so nasty
            # hack instead.
            short_description = (
                self.snapshot.description
                if len(self.snapshot.description) < MAX_DESCRIPTION_LENGTH else
                (
                    self.snapshot.description[
                        :MAX_DESCRIPTION_LENGTH - len(ELLIPSIS)] + ELLIPSIS)
            )

            snapped_images = (
                "[snapped images]" if self.entry.copy_images else "")

            return (
                "{short_description} "
                "({self.snapshot.iso_timestamp}){snapped_images}").format(
                    self=self,
                    snapped_images=snapped_images,
                    short_description=short_description)

        def __getattr__(self, name):
            if hasattr(self.snapshot, name):
                return getattr(self.snapshot, name)

            if hasattr(self.entry, name):
                return getattr(self.entry, name)

            raise AttributeError(name)

    def __init__(self, snapshot, config):
        self.snapshot = snapshot
        self.config = config

    @property
    def kernel_image_name(self):
        if self.copy_images:
            return "vmlinuz-linux-{snapshot.num}".format(
                snapshot=self.snapshot)
        else:
            return "vmlinuz-linux"

    @property
    def initramfs_image_name(self):
        if self.copy_images:
            return "initramfs-linux-{snapshot.num}.img".format(
                snapshot=self.snapshot)
        else:
            return "initramfs-linux.img"

    @property
    def image_dir(self):
        if self.copy_images:
            return Path("/") / self.config.images_snapshot_dir
        else:
            return Path("/")

    @property
    def kernel_image_path(self):
        return self.image_dir / self.kernel_image_name

    @property
    def initramfs_image_path(self):
        return self.image_dir / self.initramfs_image_name

    @property
    def copy_images(self):
        return strtobool(
            self.snapshot.userdata.get("copy_images", "false")
        )

    @property
    def subvol(self):
        return (
            self.config.root_subvolume /
            ".snapper_systemd_boot/{self.snapshot.num}".format(
                self=self)
        )

    def get_contents(self):
        ctx = self.EntryTemplateContext(entry=self, snapshot=self.snapshot)
        return self.config.entry_template.format(entry=ctx)

    def get_entry_path(self):
        name = "{config.entry_prefix}{snapshot.num}.conf".format(
            config=self.config, snapshot=self.snapshot)
        return self.config.systemd_entries_path / name

    def write(self):
        with open(self.get_entry_path(), 'w') as output:
            output.write(self.get_contents())


class SnapperSystemDBootManager:
    """
    Manage systemd-boot entries derived from snapper snapshots.

    TODO: Make the writable snapshot generation easier to safely test.
    TODO: Make the kernel and initramfs generation easier to safely test.
    """

    def __init__(self, snapper, config):
        self.snapper = snapper
        self.config = config

    def get_root_config(self):
        for config in self.snapper.get_configs_iter():
            if config.path == Path("/"):
                return config
        raise KeyError("Unable to find root config.")

    def get_snapshots_iter(self):
        config = self.get_root_config()
        for snapshot in self.snapper.get_snapshots_iter(config.name):
            if snapshot.description == "current":
                continue
            if "bootable" in snapshot.userdata:
                is_bootable = strtobool(snapshot.userdata["bootable"].lower())
                if not is_bootable:
                    continue

            yield snapshot

    def get_boot_entries(self):
        for snapshot in self.get_snapshots_iter():
            yield BootEntry(snapshot, self.config)

    def write_boot_entries(self):
        DEV_LOGGER.info("Writing new entries...")
        for entry in self.get_boot_entries():
            DEV_LOGGER.info("Writing: %r", entry)
            entry.write()
            writable_snapshot_dir = Path("/.snapper_systemd_boot")
            writable_snapshot_dir.mkdir(exist_ok=True)
            writable_snapshot_path = (
                writable_snapshot_dir / str(entry.snapshot.num))
            sh.btrfs.subvolume.snapshot(
                entry.snapshot.mount_point, writable_snapshot_path)

            if entry.copy_images:
                DEV_LOGGER.info("Copying images")

                snapshot_dir = self.config.images_snapshot_dir_full
                snapshot_dir.mkdir(exist_ok=True)

                # Copy vmlinux
                linux_src = (
                    entry.snapshot.mount_point /
                    self.config.kernel_image_source
                )
                linux_dst = snapshot_dir / entry.kernel_image_name
                shutil.copyfile(linux_src, linux_dst)

                # Copy initramfs
                initramfs_src = (
                    entry.snapshot.mount_point /
                    self.config.initramfs_image_source
                )
                initramfs_dst = snapshot_dir / entry.initramfs_image_name
                shutil.copyfile(initramfs_src, initramfs_dst)

    def get_existing_entries(self):
        glob = "{config.entry_prefix}*.conf".format(config=self.config)
        return self.config.systemd_entries_path.glob(glob)

    def remove_boot_configs(self):
        for p in self.get_existing_entries():
            DEV_LOGGER.info("Removing: %s", p)
            p.unlink()

        writable_snapshot_dir = Path("/.snapper_systemd_boot")
        if writable_snapshot_dir.is_dir():
            for p in writable_snapshot_dir.iterdir():
                DEV_LOGGER.info("Remove writable snapshot: %s")
                assert p.is_dir()
                sh.btrfs.subvolume.delete(p)
            writable_snapshot_dir.rmdir()

        if self.config.images_snapshot_dir_full.is_dir():
            DEV_LOGGER.info(
                "Removing directory: %s", self.config.images_snapshot_dir_full)
            shutil.rmtree(self.config.images_snapshot_dir_full)
