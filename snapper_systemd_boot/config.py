from pathlib import Path
import configparser

from reprutils import GetattrRepr


class SnapperSystemDBootConfig:
    def __init__(
            self,
            *ignore,
            image_source_path,
            systemd_entries_path,
            entry_prefix,
            entry_template,
            ):
        assert not ignore

        self.image_source_path = Path(image_source_path)
        assert self.image_source_path.is_dir()

        self.systemd_entries_path = Path(systemd_entries_path)
        assert self.systemd_entries_path.is_dir()

        self.entry_prefix = entry_prefix
        self.entry_template = entry_template

    @classmethod
    def from_filename(cls, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        section = config["DEFAULT"]
        return cls(
            image_source_path=section["IMAGES_SOURCE"],
            systemd_entries_path=section["SYSTEMD_ENTRIES"],
            entry_prefix=section["ENTRY_PREFIX"],
            entry_template=section["ENTRY_TEMPLATE"])

    __repr__ = GetattrRepr(
        image_source_path="image_source_path",
        systemd_entries_path="systemd_entries_path",
        entry_prefix="entry_prefix",
        entry_template="entry_template",
    )
