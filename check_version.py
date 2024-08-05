import sys

import upgrade


def compare_version_number(version_to_check):
    latest_version, _ = upgrade.UPGRADE_STEPS[-1]

    if latest_version == version_to_check:
        return 0
    else:
        return 1


if __name__ == "__main__":
    version_to_check = str(sys.argv[1])
    sys.exit(compare_version_number(version_to_check))
