"""Utility functions that deal with USB sticks."""

from typing import List

import subprocess
import os


EXPORT_DIR_NAME = "Patienten"


def get_usb_dirs() -> List[str]:
    """Return the mount point (directory) of a mounted USB stick.

    If multiple USB sticks are pugged in, the retun order will be /sda to /sdz
        (first plugged in to last plugged in for the first 26 USB sticks)

    Returns:
        List[str]: A list of paths that USB partitions are mounted to.
    """
    p = subprocess.Popen(["df", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()

    drives: List[str]

    title_row, *drives = output.decode().split("\n")

    # Since we're on a raspberry pi, /dev/sd<x> will only return USB sticks
    # sorted() to order /dev/sda before /dev/sdb etc. (Might be unnecessary)
    usb_drives: List[str] = sorted(
        [drive for drive in drives if drive.startswith("/dev/sd")]
    )

    usb_mount_points: List[str] = []

    for d in usb_drives:
        usb_mount_points.append(d[title_row.lower().index("%") + 2 :])

    return usb_mount_points


def get_export_dir() -> str:
    """Return the path of a directory on a USB stick exports can be saved in.

    This will always take the first partition on the USB stick that was plugged
        in first (<26 USB sticks). If such a directory does not exist on the
        partition, it is created.

    Returns:
        str: The absolute path of the export directory

    Raises:
        IOError: If no USB stick is plugged in
    """
    usb_dirs: List[str] = get_usb_dirs()

    if len(usb_dirs) < 1:
        raise IOError("No USB stick plugged in")

    export_dir_path: str = os.path.join(usb_dirs[0], EXPORT_DIR_NAME)

    subprocess.call(("mkdir", "-p", export_dir_path))

    return export_dir_path


if __name__ == "__main__":
    print(get_export_dir())
