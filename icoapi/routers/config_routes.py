import logging
import os

import yaml
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette.responses import FileResponse

from icoapi.scripts.config_helper import (
    ALLOWED_YAML_CONTENT_TYPES,
    store_metadata_file,
    validate_metadata_payload,
)
from icoapi.scripts.errors import (
    HTTP_400_INVALID_YAML_EXCEPTION,
    HTTP_400_INVALID_YAML_SPEC,
    HTTP_404_FILE_NOT_FOUND_EXCEPTION,
    HTTP_404_FILE_NOT_FOUND_SPEC,
    HTTP_415_UNSUPPORTED_YAML_MEDIA_TYPE_EXCEPTION,
    HTTP_415_UNSUPPORTED_YAML_MEDIA_TYPE_SPEC,
    HTTP_422_METADATA_SCHEMA_EXCEPTION,
    HTTP_422_METADATA_SCHEMA_SPEC,
    HTTP_500_METADATA_WRITE_EXCEPTION,
    HTTP_500_METADATA_WRITE_SPEC,
)
from icoapi.scripts.file_handling import get_config_dir

router = APIRouter(
    prefix="/config",
    tags=["Configuration"]
)

logger = logging.getLogger(__name__)


@router.get("/meta", responses={
    200: { "description": "File was found and returned." },
    404: HTTP_404_FILE_NOT_FOUND_SPEC
})
async def get_metadata_file(config_dir: str = Depends(get_config_dir)):
    try:
        return FileResponse(
            os.path.join(config_dir, "metadata.yaml"),
            media_type="application/x-yaml",
            filename="metadata.yaml",
        )
    except FileNotFoundError:
        raise HTTP_404_FILE_NOT_FOUND_EXCEPTION


@router.post(
    "/meta",
    responses={
        200: {"description": "Metadata configuration uploaded successfully."},
        400: HTTP_400_INVALID_YAML_SPEC,
        415: HTTP_415_UNSUPPORTED_YAML_MEDIA_TYPE_SPEC,
        422: HTTP_422_METADATA_SCHEMA_SPEC,
        500: HTTP_500_METADATA_WRITE_SPEC,
    },
)
async def upload_metadata_file(
    metadata_file: UploadFile = File(description="YAML metadata configuration file"),
    config_dir: str = Depends(get_config_dir),
):
    if metadata_file.content_type and metadata_file.content_type.lower() not in ALLOWED_YAML_CONTENT_TYPES:
        raise HTTP_415_UNSUPPORTED_YAML_MEDIA_TYPE_EXCEPTION

    raw_content = await metadata_file.read()
    if not raw_content:
        logger.error("Received empty YAML payload for metadata upload")
        raise HTTP_400_INVALID_YAML_EXCEPTION

    try:
        parsed_yaml = yaml.safe_load(raw_content)
    except yaml.YAMLError as exc:
        logger.error(f"Failed to parse uploaded metadata YAML: {exc}")
        raise HTTP_400_INVALID_YAML_EXCEPTION

    if parsed_yaml is None:
        errors = ["YAML document must not be empty"]
    else:
        errors = validate_metadata_payload(parsed_yaml)

    if errors:
        logger.error(f"Metadata YAML validation failed: {errors}")
        error_detail = f"{HTTP_422_METADATA_SCHEMA_EXCEPTION.detail} Errors: {'; '.join(errors)}"
        raise HTTPException(
            status_code=HTTP_422_METADATA_SCHEMA_EXCEPTION.status_code,
            detail=error_detail,
        )

    try:
        backup_path, metadata_path = store_metadata_file(raw_content, config_dir)
    except OSError as exc:
        logger.exception(f"Failed to store metadata configuration in {config_dir}")
        raise HTTP_500_METADATA_WRITE_EXCEPTION from exc

    if backup_path:
        logger.info(f"Existing metadata.yaml moved to backup at {backup_path}")
    else:
        logger.info(f"No existing metadata.yaml found in {config_dir}; storing new file")

    logger.info(f"Metadata configuration saved to {metadata_path}")
    return {"detail": "Metadata configuration uploaded successfully."}





