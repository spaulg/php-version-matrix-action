import threading
import logging

from . import release_versions
from . import constant


def build_matrix(extra_matrix: dict | None = None) -> dict:
    """
    Build the version matrix

    :param extra_matrix: Optional extra matrix data to deep-merge into the result
    :return: dict
    """

    threads = []
    matrix = {"version": [], "include": []}
    if extra_matrix:
        _deep_merge_into(matrix, extra_matrix)

    failures = []

    for version in release_versions.list_all_versions():
        logging.info("Spawning check for version %s", version)

        thread = threading.Thread(
            target=_check_version,
            args=(version, matrix, failures),
            name="BuildThread-" + version
        )

        threads.append(thread)
        thread.start()

    logging.info("Waiting for all threads to finish...")
    for thread in threads:
        thread.join()

    # Sort versions
    matrix["version"].sort()

    return matrix


def _deep_merge_into(target: dict, incoming: dict) -> dict:
    """
    Deep-merge `incoming` into `target` (mutates `target`).

    Rules:
      - dict + dict  => recursive merge
      - list + list  => extend target list with incoming list
      - otherwise    => overwrite target with incoming
    """

    for key, incoming_value in incoming.items():
        if key not in target:
            target[key] = incoming_value
            continue

        target_value = target[key]

        if isinstance(target_value, dict) and isinstance(incoming_value, dict):
            _deep_merge_into(target_value, incoming_value)
        elif isinstance(target_value, list) and isinstance(incoming_value, list):
            target_value.extend(incoming_value)
        else:
            target[key] = incoming_value

    return target


def _check_version(version_number: str, matrix: dict, failures: list):
    """
    Check a particular version for freshness

    :param version_number:
    :param matrix:
    :param failures:
    :param :username:
    :param password:
    :param repository:
    :return:
    """

    try:
        version_metadata = release_versions.fetch_version_metadata(version_number)
        logging.debug(version_metadata)

        _append_version_entry(
            version_metadata,
            matrix,
        )

        _append_version_entry(
            version_metadata,
            matrix,
            "zts",
        )

    except Exception:
        failures.append(version_number)


def _append_version_entry(version_metadata: dict, matrix: dict, suffix: str = None):
    """
    Append the desired version to the version matrix with the optional suffix

    :param version_metadata:
    :param matrix:
    :param epoch:
    :param suffix:
    :return:
    """

    metadata = ""
    if suffix is not None:
        metadata = "+" + suffix

    matrix["version"].append(version_metadata["short_version"] + metadata)
    matrix["include"].append({
        "version": version_metadata["short_version"] + metadata,
        "full_sem_version": version_metadata["full_version"] + metadata,
        "short_version": version_metadata["short_version"],
    })
