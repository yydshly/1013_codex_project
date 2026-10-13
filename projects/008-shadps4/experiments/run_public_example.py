"""Prepare and run official OpenOrbis public samples with shadPS4 on Windows.

Only downloads public open-source releases. No Sony modules or commercial games.
All downloads, generated binaries, configuration, and new run logs stay in runtime/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "runtime"
PACKAGES = (
    (
        "shadps4-win64-sdl-0.19.0.zip",
        "https://github.com/shadps4-emu/shadPS4/releases/download/v.0.19.0/",
        "b9600602a809b7cb4aaf29cbeb0917d32caecf27bc5a9232df76200fbf80c017",
        "shadps4",
    ),
    (
        "samples-elf-llvm-18.zip",
        "https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/releases/download/v0.5.3/",
        "26e32c08ebdccd428a34cf9f22a89967bbac6359e411fbf73957b8d543c4ca68",
        "openorbis-samples",
    ),
    (
        "toolchain-llvm-18.2.zip",
        "https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/releases/download/v0.5.3/",
        "5006bb8629a40093b712fac971456fa4d5ad3fafaadb16d11c10b8a93b8b496f",
        "openorbis-toolchain",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_member(destination: Path, member: str) -> None:
    if not (destination / member).resolve().is_relative_to(destination.resolve()):
        raise ValueError(f"Archive member escapes runtime directory: {member}")


def prepare() -> tuple[Path, Path]:
    RUNTIME.mkdir(exist_ok=True)
    for filename, prefix, expected, folder in PACKAGES:
        archive = RUNTIME / filename
        if not archive.exists():
            print(f"Downloading official public release: {filename}", flush=True)
            urllib.request.urlretrieve(prefix + filename, archive)
        actual = sha256(archive)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {filename}: {actual}")
        print(f"SHA-256 verified: {filename}", flush=True)
        destination = RUNTIME / folder
        destination.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive) as package:
            for member in package.infolist():
                check_member(destination, member.filename)
            package.extractall(destination)

    toolchain_container = RUNTIME / "openorbis-toolchain"
    toolchain = toolchain_container / "OpenOrbis" / "PS4Toolchain"
    converter = toolchain / "bin" / "windows" / "create-fself.exe"
    if not converter.exists():
        with tarfile.open(toolchain_container / "toolchain-llvm-18.tar.gz") as package:
            members = package.getmembers()
            for member in members:
                check_member(toolchain_container, member.name)
                if member.issym() or member.islnk():
                    check_member(toolchain_container, member.linkname)
            # Official toolchain contains no absolute output paths.
            # Python 3.12+ also applies its data extraction filter.
            if sys.version_info >= (3, 12):
                package.extractall(toolchain_container, filter="data")
            else:
                package.extractall(toolchain_container)
    if not converter.exists():
        raise FileNotFoundError("Official Windows OpenOrbis converter not found")

    environment = os.environ.copy()
    environment["OO_PS4_TOOLCHAIN"] = str(toolchain)
    for sample, folder in (("hello_world", "public-hello"), ("graphics", "public-graphics")):
        sample_elf = RUNTIME / "openorbis-samples" / "samples" / sample / sample / "x64" / "Debug" / f"{sample}.elf"
        output = RUNTIME / folder
        output.mkdir(exist_ok=True)
        subprocess.run(
            [str(converter), "-in", str(sample_elf), "-out", str(output / f"{sample}.oelf"), "-eboot", str(output / "eboot.bin")],
            env=environment,
            check=True,
        )
        print(f"Prepared public PS4 sample: {sample}", flush=True)
    return RUNTIME / "shadps4" / "shadPS4.exe", RUNTIME / "public-graphics" / "eboot.bin"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", choices=("hello_world", "graphics"), default="graphics")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--seconds", type=float, default=0, help="Stop after N seconds; 0 waits until the window closes")
    parser.add_argument("--driver-select", default="", help="Optional process-local Vulkan driver filter; this machine was verified with *nv*")
    options = parser.parse_args()
    if os.name != "nt":
        parser.error("This reproduction uses the official Windows release")
    if options.seconds < 0:
        parser.error("--seconds must be non-negative")
    executable, _ = prepare()
    if options.prepare_only:
        print("Ready. Use --sample graphics to open the public Mandelbrot example.")
        return

    user_directory = executable.parent / "user"
    user_directory.mkdir(exist_ok=True)
    config_path = user_directory / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8-sig")) if config_path.exists() else {}
    config.setdefault("GPU", {}).update({"null_gpu": options.sample == "hello_world", "full_screen": False})
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    environment = os.environ.copy()
    if options.driver_select:
        environment["VK_LOADER_DRIVERS_SELECT"] = options.driver_select
    sample_folder = "public-hello" if options.sample == "hello_world" else "public-graphics"
    sample_path = RUNTIME / sample_folder / "eboot.bin"
    stdout_path = RUNTIME / f"latest-{options.sample}-stdout.txt"
    stderr_path = RUNTIME / f"latest-{options.sample}-stderr.txt"
    with stdout_path.open("w", encoding="utf-8") as output, stderr_path.open("w", encoding="utf-8") as errors:
        process = subprocess.Popen([str(executable), "-g", str(sample_path), "-f", "false"], cwd=executable.parent, env=environment, stdout=output, stderr=errors)
        print(f"Started {options.sample}. Close its window or press Ctrl+C to stop.")
        try:
            process.wait(timeout=options.seconds or None)
        except subprocess.TimeoutExpired:
            print("Requested observation interval complete; stopping public sample.")
            process.terminate()
            process.wait(timeout=10)
        except KeyboardInterrupt:
            process.terminate()
            process.wait(timeout=10)
        finally:
            print(f"Log: {stdout_path}")
    if options.sample == "hello_world":
        text = stdout_path.read_text(encoding="utf-8", errors="replace")
        print("Guest Hello world observed:", "Hello world! Waiting 2 seconds!" in text)
    print("This public homebrew example does not verify commercial game compatibility or GCN shader recompilation.")


if __name__ == "__main__":
    main()
