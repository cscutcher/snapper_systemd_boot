from pathlib import Path
import configparser

from reprutils import GetattrRepr


class SnapperSystemDBootConfig:
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

    @classmethod
    def from_filename(cls, filename):
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
    )
