# `snapper_systemd_boot`
The aim of this tool is to automatically create boot entries for
[systemd-boot](https://www.freedesktop.org/wiki/Software/systemd/systemd-boot/)
from snapshots created by [snapper](http://snapper.io/).

While I've tried to make this generic enough to be useful for others there are
probably places where it's currently specific to my particular environment.

If there's anything I can do to help it work for you feel free raise an issue
or submit a PR.

The primary location for this project is
[GitLab](https://gitlab.com/cscutcher/snapper_systemd_boot).
A mirror is maintained on
[github](https://github.com/cscutcher/snapper_systemd_boot)
just for visibility.

# Not production ready!
As I say this was hacked up over a weekend and is relatively untested and
specific to my requirements. I'm not even sure it's a good idea!

At least read all the `README.md`. One specific warning though **there may be
unintended consequences if snapper, or snapper_systemd_boot run while booted
into a snapshot. BUYER BEWARE!**

# Testing
I started with good intentions, but I've been really naughty with the testing.

Early on I was using a lot of pre-canned tests to help me develop the thing but
I didn't have time to invest in mocking out DBUS or btrfs functions so most of
the tests expect real config and call out to real snapper or btrfs.

Some even write to disk in a way that may be dangerous.

I've marked tests appropriately and you can see which groups to run with;

```
pytest --markers
```

running tests with;

```
pytest -m "not dangerous" --pylama"
```

is safe, if not particularly comprehensive, and what I do most the time.

It'd be nice to have some integration tests. I think I might be able to do
something with a docker container (it'd probably need privileged to work)
or maybe LXC containers, but I haven't had much chance to play with the latter.

The lack of decent testing is obviously and obstruction to any reasonable CI
attempt.

# My environment
So that others can understand how to use this tool and design decisions.

* [Arch Linux](https://www.archlinux.org/) (from an
  [Antergos](https://antergos.com/) install).
* UEFI boot (with systemd-boot obviously).
* Python 3.6
* Snapper
* `/boot` is not on btrfs. This isn't possible with uefi.
* Using
  [pacman-boot-backup-hook from aur](https://aur.archlinux.org/packages/pacman-boot-backup-hook/).

# How to use

### Installation
1. Install python package. If you only want to manually trigger updates then a
   virtualenv or `--user` installation will suffice.
   However global installation is advised.
2. Use example config to create `/etc/snapper_systemd_boot.conf`
3. Add crontab entry to update entries at regular intervals.
   Unfortunately there appears not to be hooks for snapper to allow this to be
   triggered automatically after snapshot creation.

### Running
If hooks are installed then nothing else is required there are some useful
manual commands though.  Run `snapper-systemd-boot --help` for more information.

Note that when new boot entries are generated the tool will also;

* Create a number of additional btrfs snapshots (see booting section below).
* Potentially copy additional kernel and initramfs images to boot partition
  (see "Including kernel image and initramfs").

### Booting into snapshot
When booting into one of the snapper snapshots you are actually booting into a
writable copy of the initial snapshot.

**Changes are only preserved until the next time the tool updates boot entries**

at which time these writable snapshots are all erased and recreated.

### Which snapshots are included
Currently all snapshots apart from "current" are included unless the following
is specified in metadata;

```
bootable = false
```


### Including kernel image and initramfs
Because `/boot`, where the kernel and the initaramfs image reside,
snapper won't directly snapshot either of these.

Pacman scripts can be used to copy `/boot` to a location on the btrfs root
partition when the kernel is updated.
I personally use this
[AUR package](https://aur.archlinux.org/packages/pacman-boot-backup-hook/).

However this doesn't allow us to boot using those backed up kernel and initramfs
image as they are inaccessible at boot.
Equally, I didn't want to copy every single image to the boot partition that'd
eat a lot of space on fat partition UEFI uses.

I wanted to have the option to copy the kernal and initramfs image for some
snapshots. This is possible by specifying the following metadata when creating
a snapshot;

```
bootable = true
copy_images = true
```

**If the `copy_images` parameter isn't used then booting will always use the
most recent kernal and initramfs.**

For many classes of problem this should good enough to boot into a snapshot and
fix an issue, but its probably a good idea to have at least one snapshot using
`copy_images` so you can always reliably boot.


# TODO
* Protection around snapper or `snapper_systemd_boot` running while booted into
  snapshot.
* Ability to test functionality around btrfs and snapper calls.
* Reduce number of pip pre-requisites;
    * While I quite like `reprutils` as a way to cleanly define a `repr`
      that's std compliant, I could probably do without it.
    * My limited use of the `sh` equally could probably be replaced with stdlib.
* Package on Pypi
* AUR package
* CI
* On update all entries are remove before being recreated, this leaves a window
  in which something going wrong could leave us without boot entries.
