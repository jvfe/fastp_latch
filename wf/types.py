from dataclasses import dataclass
from typing import Optional, Union

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


@dataclass_json
@dataclass
class FastpInput:
    sample: Union[PairedEnd, SingleEnd]
    quality_threshold: int
    adapter_fasta: Optional[LatchFile]
    adapter_string: Optional[str]
    read_type: str
