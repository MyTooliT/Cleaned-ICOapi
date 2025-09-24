from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Tuple, Union

ALLOWED_YAML_CONTENT_TYPES = {
    "application/x-yaml",
    "application/yaml",
    "text/yaml",
    "text/x-yaml",
    "application/octet-stream",
    "text/plain",
}

FIELD_DEFINITION_REQUIRED_KEYS = {"id", "label", "datatype", "type"}

METADATA_FILENAME = "metadata.yaml"
METADATA_BACKUP_DIRNAME = "backup"
BACKUP_TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"

PathLike = Union[str, Path]


def validate_metadata_payload(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Root document must be a mapping"]

    info = payload.get("info")
    if not isinstance(info, dict):
        errors.append("info: expected mapping with metadata info")
    else:
        version = info.get("version")
        if not isinstance(version, str) or not version.strip():
            errors.append("info -> version: expected non-empty string")

    profiles = payload.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        errors.append("profiles: expected at least one profile definition")
    else:
        for profile_key, profile_value in profiles.items():
            errors.extend(validate_profile(profile_key, profile_value))

    return errors


def validate_profile(profile_key: str, profile_value: dict) -> list[str]:
    path_prefix = f"profiles -> {profile_key}"
    errors: list[str] = []

    if not isinstance(profile_value, dict):
        errors.append(f"{path_prefix}: expected mapping with profile configuration")
        return errors

    for field_name in ("id", "name"):
        field_value = profile_value.get(field_name)
        if not isinstance(field_value, str) or not field_value.strip():
            errors.append(f"{path_prefix} -> {field_name}: expected non-empty string")

    for stage in ("pre", "post"):
        if stage in profile_value:
            section = profile_value[stage]
            if not isinstance(section, dict):
                errors.append(f"{path_prefix} -> {stage}: expected mapping of sections")
            else:
                validate_sections(section, ["profiles", str(profile_key), stage], errors)

    return errors


def validate_sections(section: dict, path: list[str], errors: list[str]) -> None:
    if not isinstance(section, dict):
        errors.append(" -> ".join(path) + ": expected mapping")
        return

    for key, value in section.items():
        current_path = path + [str(key)]
        if not isinstance(value, dict):
            errors.append(f" -> ".join(current_path) + ": expected mapping for field definition or nested section")
            continue

        if is_field_definition(value):
            validate_field_definition(value, current_path, errors)
        else:
            validate_sections(value, current_path, errors)


def is_field_definition(value: dict[str, Any]) -> bool:
    return FIELD_DEFINITION_REQUIRED_KEYS.issubset(value.keys())


def validate_field_definition(field: dict[str, Any], path: list[str], errors: list[str]) -> None:
    for key in FIELD_DEFINITION_REQUIRED_KEYS:
        field_value = field.get(key)
        if not isinstance(field_value, str) or not field_value.strip():
            errors.append(" -> ".join(path + [key]) + ": expected non-empty string")

    options = field.get("options")
    if options is not None and not isinstance(options, list):
        errors.append(" -> ".join(path + ["options"]) + ": expected list when provided")


def store_metadata_file(content: bytes, config_dir: PathLike) -> Tuple[Optional[Path], Path]:
    config_path = Path(config_dir)
    config_path.mkdir(parents=True, exist_ok=True)

    metadata_path = config_path / METADATA_FILENAME
    backup_path: Optional[Path] = None

    if metadata_path.exists():
        backup_path = move_metadata_to_backup(metadata_path)

    metadata_path.write_bytes(content)
    return backup_path, metadata_path


def move_metadata_to_backup(metadata_path: Path) -> Path:
    backup_dir = metadata_path.parent / METADATA_BACKUP_DIRNAME
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(BACKUP_TIMESTAMP_FORMAT)

    suffix = ''.join(metadata_path.suffixes)
    base_name = metadata_path.name[:-len(suffix)] if suffix else metadata_path.name

    backup_path = backup_dir / f"{base_name}__{timestamp}{suffix}"

    counter = 1
    while backup_path.exists():
        backup_path = backup_dir / f"{base_name}__{timestamp}_{counter}{suffix}"
        counter += 1

    metadata_path.replace(backup_path)
    return backup_path
