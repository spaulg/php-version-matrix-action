import logging
import argparse
import sys
import os
import json
import yaml

from version_matrix import matrix_builder

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", "-v", action="count", default=0)
parser.add_argument(
    "--extra-matrix-yaml-file",
    default="",
    help="Path to a YAML file containing extra matrix data to deep-merge into the generated matrix.",
)
args = parser.parse_args()

log_level = logging.WARNING - (2 if args.verbose > 2 else args.verbose) * 10
log_format = "%(asctime)s [%(levelname)s]: %(message)s [%(threadName)s]"
logging.basicConfig(format=log_format, level=log_level, datefmt="%H:%M:%S", stream=sys.stderr)

extra_matrix = None
if args.extra_matrix_yaml_file:
    try:
        with open(args.extra_matrix_yaml_file, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)  # can be None if file is empty
        if loaded is not None and not isinstance(loaded, dict):
            raise ValueError("extra matrix YAML must be a mapping/object at the top level.")
        extra_matrix = loaded
    except Exception as exc:
        raise SystemExit(f"Invalid extra matrix YAML file: {exc}")

matrix = matrix_builder.build_matrix(extra_matrix=extra_matrix)

print(json.dumps(matrix))
