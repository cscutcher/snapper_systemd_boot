"""
Module to access config for snapper_systemd_boot.

This is a bit of a mess. I was trying to keep it simple, but as it's grown
it might need refactoring to reduce the duplication and make the validation
more obvious.

TODO: Cleanup this module. Use some schema based library maybe like Colander or
      zope.schema.
"""
from pathlib import Path
import configparser

from reprutils import GetattrRepr
import pytest


@pytest.mark.real_config
def test_load_example_config():
    """
    Test loading the example config.

    TODO: Add some assertions.
    TODO: While loading the example config is a useful validation that the
          makes sense, the validation following the load checks real file
          locations hence the `real_config` test marker.
          I could make the example config less "real" and use temporary
          directories that could be pregenerated but that makes the example
          less useful.
    """
    config = SnapperSystemDBootConfig.from_filename(
        "snapper_systemd_boot.conf.example")
    print(config)


class SnapperSystemDBootConfig:
    """
    Stores config for SnapperSystemDBootConfig.

    See example config for description of what fields do.
    """
    def __init__(
            self,
            *ignore,
            systemd_entries_path,
            entry_prefix,
            entry_template,
            kernel_image_source,
            initramfs_image_source,
            images_snapshot_dir,
            boot_path,
            root_subvolume,
            ):
        assert not ignore

        self.kernel_image_source = Path(kernel_image_source)
        assert not self.kernel_image_source.is_absolute()

        self.initramfs_image_source = Path(initramfs_image_source)
        assert not self.initramfs_image_source.is_absolute()

        self.systemd_entries_path = Path(systemd_entries_path)
        assert self.systemd_entries_path.is_dir()

        self.boot_path = Path(boot_path)
        assert self.boot_path.is_dir()

        self.entry_prefix = entry_prefix
        self.entry_template = entry_template
        self.images_snapshot_dir = Path(images_snapshot_dir)

        self.images_snapshot_dir_full = (
            self.boot_path / self.images_snapshot_dir
        )

        self.root_subvolume = Path(root_subvolume)

    @classmethod
    def from_filename(cls, filename):
        """
        Load config from INI at given filename.
        """
        config = configparser.ConfigParser()
        config.read(filename)
        section = config["DEFAULT"]
        return cls(**section)

    __repr__ = GetattrRepr(
        systemd_entries_path="systemd_entries_path",
        entry_prefix="entry_prefix",
        entry_template="entry_template",
        kernel_image_source="kernel_image_source",
        initramfs_image_source="initramfs_image_source",
        images_snapshot_dir="images_snapshot_dir",
        boot_path="boot_path",
        root_subvolume="root_subvolume",
    )
