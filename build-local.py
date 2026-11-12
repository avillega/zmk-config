#!/usr/bin/env python3
"""Build the GitHub Actions matrix locally, with a separate log per target."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import subprocess
import sys

import yaml

root = Path(__file__).resolve().parent
matrix = yaml.safe_load((root / "build.yaml").read_text())
targets = matrix["include"]
if set(matrix) != {"include"} or not targets or any(set(target) != {"board", "shield"} for target in targets):
    sys.exit("build-local.py only supports board and shield entries in build.yaml")
names = [f'{target["shield"]}-{target["board"]}' for target in targets]
if len(set(names)) != len(names):
    sys.exit("build.yaml contains duplicate build targets")
(root / "build").mkdir(exist_ok=True)
env = os.environ.copy()
env.setdefault("CMAKE_BUILD_PARALLEL_LEVEL", "2")


def build(target):
    name = f'{target["shield"]}-{target["board"]}'
    log = root / "build" / f"{name}.log"
    command = [
        "west", "build", "-s", "zmk/app", "-d", f"build/{name}",
        "-b", target["board"], "--", f"-DZMK_CONFIG={root / 'config'}",
        f'-DSHIELD={target["shield"]}',
    ]
    with log.open("w") as output:
        result = subprocess.run(command, cwd=root, env=env, stdout=output, stderr=subprocess.STDOUT)
    if result.returncode:
        print(f"FAILED {name}: {log}", flush=True)
    else:
        print(f"OK {name}: build/{name}/zephyr/zmk.uf2", flush=True)
    return result.returncode


with ThreadPoolExecutor(max_workers=len(targets)) as executor:
    results = list(executor.map(build, targets))
sys.exit(any(results))
