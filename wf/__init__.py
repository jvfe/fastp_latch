import re
from pathlib import Path
from typing import Optional

from latch import medium_task, message, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchDir, LatchFile

from .docs import fastp_docs
from .types import PairedEnd, SingleEnd
from .utils import _capture_output


@medium_task
def run_fastp(
    paired_end: PairedEnd,
    quality_threshold: int,
    single_end: Optional[SingleEnd],
    adapter_fasta: Optional[LatchFile],
    adapter_string: Optional[str],
) -> LatchDir:
    """Adapter removal and read trimming with fastp"""

    sample = single_end if single_end is not None else paired_end
    read_type = "single" if sample == single_end else "paired"

    message(
        "info",
        {"title": "Set fastp mode", "info": f"Running fastp in {read_type}-end mode."},
    )

    sample_name = sample.name
    output_dir = Path("fastp_results").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    output_prefix = f"{str(output_dir)}/{sample_name}"

    out1_name = (
        f"{output_prefix}.trim.fastq.gz"
        if read_type == "single"
        else f"{output_prefix}_1.trim.fastq.gz"
    )

    _fastp_cmd = [
        "/root/fastp",
        "--in1",
        sample.read1.local_path,
        "--out1",
        out1_name,
        "--json",
        f"{output_prefix}.fastp.json",
        "--html",
        f"{output_prefix}.fastp.html",
        "--thread",
        "16",
        "--qualified_quality_phred",
        str(quality_threshold),
    ]

    if read_type == "paired":
        _fastp_cmd.extend(
            [
                "--in2",
                sample.read2.local_path,
                "--out2",
                f"{output_prefix}_2.trim.fastq.gz",
            ]
        )

    # Handle adapter content
    if adapter_fasta is not None:
        _fastp_cmd.extend(["--adapter_fasta", adapter_fasta.local_path])
    elif adapter_string is not None:
        _fastp_cmd.extend(["--adapter_sequence", adapter_string])
    else:
        message(
            "warning",
            {
                "title": "Automatic adapter removal option chosen",
                "body": (
                    "Be aware that letting fastp automatically detect adapter"
                    " sequences can lead to worse results."
                ),
            },
        )

        if read_type == "paired":
            _fastp_cmd.append("--detect_adapter_for_pe")

    running_cmd = " ".join(_fastp_cmd)

    message(
        "info",
        {
            "title": f"Running fastp for input {sample_name}",
            "body": f"Command: {running_cmd}",
        },
    )

    return_code, stdout = _capture_output(_fastp_cmd)

    if return_code != 0:
        errors = re.findall("ERROR.*", stdout[1])

        for error in errors:
            message(
                "error",
                {
                    "title": f"An error was raised while running fastp for {sample_name}",
                    "body": error,
                },
            )

    return LatchDir(str(output_dir), f"latch:///fastp_results/{sample_name}")


@workflow(fastp_docs)
def fastp(
    sample_fork: str,
    paired_end: PairedEnd,
    quality_threshold: int = 30,
    adapter_fork: str = "none",
    adapter_fasta: Optional[LatchFile] = None,
    adapter_string: Optional[str] = None,
    single_end: Optional[SingleEnd] = None,
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
    return run_fastp(
        paired_end=paired_end,
        single_end=single_end,
        quality_threshold=quality_threshold,
        adapter_fasta=adapter_fasta,
        adapter_string=adapter_string,
    )


LaunchPlan(
    fastp,
    "Test Data",
    {
        "paired_end": PairedEnd(
            name="SRR579292",
            read1=LatchFile("s3://latch-public/test-data/4318/SRR579292_1.fastq"),
            read2=LatchFile("s3://latch-public/test-data/4318/SRR579292_2.fastq"),
        ),
        "quality_threshold": 30,
        "adapter_fasta": LatchFile(
            "s3://latch-public/test-data/4318/sample_adapters.fa"
        ),
    },
)
