# This file is auto-generated from metadata.yaml
from dataclasses import dataclass
from enum import Enum
from typing import Optional

METADATA_VERSION = '0.0.1'

@dataclass
class Quantity:
    value: float
    unit: str

class ProcessEnum(str, Enum):
    MILLING = 'milling'
    DRILLING = 'drilling'
    GRINDING = 'grinding'
    TURNING = 'turning'
    REAMING = 'reaming'
    SHAPING = 'shaping'
    THREAD_CUTTING = 'thread_cutting'
    THREAD_MILLING = 'thread_milling'
    THREAD_FORMING = 'thread_forming'

class InstitutionEnum(str, Enum):
    TU_WIEN = 'TU Wien'
    TU_DARMSTADT = 'TU Darmstadt'

class ActivityEnum(str, Enum):
    TOOL_WEAR_MONITORING = 'Tool Wear Monitoring'

class WorkpieceMaterialEnum(str, Enum):
    C45 = 'C45'
    STEEL__GENERIC_ = 'Steel (generic)'

class ToolMaterialEnum(str, Enum):
    CARBIDE__P40_ = 'Carbide (P40)'
    CARBIDE = 'Carbide'
    MCD = 'MCD'
    CERAMIC = 'Ceramic'
    PCD = 'PCD'

class CoolantEnum(str, Enum):
    DRY = 'Dry'
    AIR = 'Air'
    MMQ = 'MMQ'
    FLOOD = 'Flood'
    OIL = 'Oil'

@dataclass
class UnifiedMetadata:
    person: str
    institution: InstitutionEnum
    machine: str
    experiment: str
    process: ProcessEnum
    activity: ActivityEnum
    workpiece_material: WorkpieceMaterialEnum|str
    cutting_speed: Quantity
    tool_material: ToolMaterialEnum|str
    coolant: CoolantEnum
    sth_mac: str
    stu_mac: str
    feed_per_tooth: Optional[Quantity] = None
    feed_per_rev: Optional[Quantity] = None
    doc_axial: Optional[Quantity] = None
    doc_radial: Optional[Quantity] = None
    doc: Optional[Quantity] = None
    workpiece_diameter: Optional[Quantity] = None
    tool_diameter: Optional[Quantity] = None
    tool_tooth_count: Optional[int] = None
    tool_offset: Optional[Quantity] = None
