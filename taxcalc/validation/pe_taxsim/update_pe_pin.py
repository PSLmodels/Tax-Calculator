"""
Updates pe_pin.json to the newest policyengine-taxsim commit and the
newest policyengine-us release.

USAGE: python update_pe_pin.py [--write] [--sha SHA] [--python X.Y]

Without --write, this script only reports which pe_pin.json entries
would change.  The new pin is resolved with uvx before anything is
written, so pe_pin.json is never changed to an unresolvable pin.

After writing a new pin, all the PE outputs must be regenerated with
run_pe.py --force and every difference must be re-examined.
"""

import argparse
import datetime
import json
import shutil
import subprocess
import sys
import urllib.request
import run_pe  # pylint: disable=import-error


GITHUB_API = "https://api.github.com/repos"
PYPI_API = "https://pypi.org/pypi"
URL_TIMEOUT = 30  # seconds


def get_json(url):
    """
    Return the decoded JSON response to an HTTP GET request for URL.
    """
    req = urllib.request.Request(
        url, headers={"User-Agent": "Tax-Calculator update_pe_pin.py"}
    )
    with urllib.request.urlopen(req, timeout=URL_TIMEOUT) as resp:
        return json.load(resp)


def newest_commit(repo_url, sha=None):
    """
    Return (sha, date) tuple for the specified SHA (or for the newest
    commit on the default branch if SHA is None) in the GitHub REPO_URL.
    """
    owner_repo = repo_url.removeprefix("https://github.com/").rstrip("/")
    api = f"{GITHUB_API}/{owner_repo}"
    if sha is None:
        sha = get_json(api)["default_branch"]
    commit = get_json(f"{api}/commits/{sha}")
    date = commit["commit"]["committer"]["date"][:10]
    return commit["sha"], date


def newest_pypi_version(package):
    """
    Return the newest version of PACKAGE released on PyPI.
    """
    return get_json(f"{PYPI_API}/{package}/json")["info"]["version"]


def uv_version():
    """
    Return the version of the uv on PATH.
    """
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is not on PATH; see README.md for setup")
    proc = subprocess.run(
        [uv, "--version"], check=True, capture_output=True, text=True
    )
    return proc.stdout.split()[1]


def candidate_pin(pin, args):
    """
    Return dictionary containing the updated pin, which is resolved with
    uvx (without a policyengine-core pin) to get the policyengine-taxsim,
    policyengine-core, and Python versions actually used.
    """
    new = dict(pin)
    sha, date = newest_commit(pin["policyengine_taxsim_repo"], args.sha)
    new["policyengine_taxsim_sha"] = sha
    new["policyengine_taxsim_sha_date"] = date
    new["policyengine_us_version"] = newest_pypi_version("policyengine-us")
    if args.python is not None:
        new["python_version"] = args.python
    sys.stderr.write("resolving the new pin with uvx\n")
    try:
        versions = run_pe.resolved_versions(new, pin_core=False)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(
            "uvx could not resolve the new pin:\n" + err.stderr
        ) from err
    new.update(versions)
    new["uv_version"] = uv_version()
    return new


def changes(old, new):
    """
    Return list of (key, old_value, new_value) tuples for the version
    entries that differ between the OLD and NEW pins.
    """
    return [
        (key, old.get(key), val)
        for key, val in new.items()
        if key != "pinned_on" and val != old.get(key)
    ]


def write_pin(pin):
    """
    Write PIN to pe_pin.json, preserving its key order and indentation.
    """
    with open(run_pe.PIN_FILE, "w", encoding="utf-8") as pfile:
        json.dump(pin, pfile, indent=4)
        pfile.write("\n")


def main():
    """
    Report (and with --write save) the newest pe_pin.json information.
    """
    parser = argparse.ArgumentParser(
        prog="python update_pe_pin.py",
        description=(
            "Updates pe_pin.json to the newest policyengine-taxsim commit "
            "and policyengine-us release (a dry run unless --write)."
        ),
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the new pin to pe_pin.json",
    )
    parser.add_argument(
        "--sha",
        default=None,
        help="pin this policyengine-taxsim commit instead of the newest",
    )
    parser.add_argument(
        "--python",
        default=None,
        metavar="X.Y",
        help="change the pinned Python version",
    )
    args = parser.parse_args()
    pin = run_pe.read_pin()
    try:
        new = candidate_pin(pin, args)
    except (RuntimeError, OSError) as err:
        sys.stderr.write(f"ERROR: {err}\n")
        return 1
    diffs = changes(pin, new)
    if not diffs:
        sys.stdout.write("pe_pin.json is already up to date\n")
        return 0
    for key, oldval, newval in diffs:
        sys.stdout.write(f"{key}: {oldval} --> {newval}\n")
    if not args.write:
        sys.stdout.write("dry run: use --write to update pe_pin.json\n")
        return 0
    new["pinned_on"] = datetime.date.today().isoformat()
    write_pin(new)
    sys.stdout.write(
        f"wrote {run_pe.PIN_FILE.name}; next steps:\n"
        "  1. regenerate all PE outputs with run_pe.py --all --force\n"
        "  2. run validate.py and re-examine every difference\n"
        "  3. update expected_differences, test_results.expect,\n"
        "     and the PE versions mentioned in README.md and SUMMARY.md\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
