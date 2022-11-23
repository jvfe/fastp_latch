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
    sample: Union[SingleEnd, PairedEnd]
    quality_threshold: int
    read_type: str


@dataclass_json
@dataclass
class FastpInputFASTA(FastpInput):
    adapter_fasta: LatchFile


@dataclass_json
@dataclass
class FastpInputString(FastpInput):
    adapter_string: str
