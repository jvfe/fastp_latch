import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dataclasses_json import dataclass_json
from latch import medium_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchDir, LatchFile

from .docs import fastp_docs


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


@medium_task
def run_fastp(
    paired_end: PairedEnd, single_end: Optional[SingleEnd] = None
) -> LatchDir:
    """Adapter removal and read trimming with fastp"""

    sample = single_end if single_end is not None else paired_end
    sample_name = sample.name
    output_dir = Path("fastp_results").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    output_prefix = f"{str(output_dir)}/{sample_name}"

    _fastp_cmd = [
        "/root/fastp",
        "--in1",
        sample.read1.local_path,
        "--out1",
        f"{output_prefix}_1.trim.fastq.gz",
        "--json",
        f"{output_prefix}.fastp.json",
        "--html",
        f"{output_prefix}.fastp.html",
        "--thread",
        "16",
    ]

    if type(sample) == PairedEnd:
        _fastp_cmd.extend(
            [
                "--in2",
                sample.read2.local_path,
                "--out2",
                f"{output_prefix}_2.trim.fastq.gz",
                "--detect_adapter_for_pe",
            ]
        )

    subprocess.run(_fastp_cmd)

    return LatchDir(str(output_dir), f"latch:///fastp_results/{sample_name}")


@workflow(fastp_docs)
def fastp(
    sample_fork: str, paired_end: PairedEnd, single_end: Optional[SingleEnd] = None
) -> LatchDir:
    """An ultra-fast all-in-one FASTQ preprocessor

    fastp
    ----

    A tool designed to provide fast all-in-one preprocessing
    for FastQ files. This tool is developed in C++ with multithreading
    supported to afford high performance [^1].

    [^1]: Shifu Chen, Yanqing Zhou, Yaru Chen, Jia Gu; fastp: an
    ultra-fast all-in-one FASTQ preprocessor, Bioinformatics, Volume 34,
    Issue 17, 1 September 2018, Pages i884–i890,
    https://doi.org/10.1093/bioinformatics/bty560
    """
    return run_fastp(paired_end=paired_end, single_end=single_end)


LaunchPlan(
    fastp,
    "Test Data",
    {
        "paired_end": PairedEnd(
            name="SRR579292",
            read1=LatchFile("s3://latch-public/test-data/4318/SRR579292_1.fastq"),
            read2=LatchFile("s3://latch-public/test-data/4318/SRR579292_2.fastq"),
        )
    },
)
