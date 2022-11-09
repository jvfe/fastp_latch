from dataclasses import dataclass

from dataclasses_json import dataclass_json
from latch.types import LatchFile


@dataclass_json
@dataclass
class SingleEnd:
    name: str
    read1: LatchFile


@dataclass_json
@dataclass
class PairedEnd:
    name: str
    read1: LatchFile
    read2: LatchFile
