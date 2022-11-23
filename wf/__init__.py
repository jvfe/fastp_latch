import re
from pathlib import Path
from typing import List, Optional, Union

from latch import map_task, medium_task, message, small_task, workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchDir, LatchFile

from .docs import fastp_docs
from .types import FastpInput, FastpInputFASTA, FastpInputString, PairedEnd, SingleEnd
from .utils import _capture_output


@small_task
def organize_fastp_inputs(
    paired_end: List[PairedEnd],
    quality_threshold: int,
    single_end: Optional[List[SingleEnd]],
    adapter_fasta: Optional[LatchFile],
    adapter_string: Optional[str],
) -> List[Union[FastpInputFASTA, FastpInputString, FastpInput]]:

    if single_end is not None:
        samples = single_end
        read_type = "single"
    else:
        samples = paired_end
        read_type = "paired"

    inputs = []
    for sample in samples:

        # TODO: Improve this
        if adapter_fasta is not None:
            cur_sample = FastpInputFASTA(
                sample=sample,
                read_type=read_type,
                adapter_fasta=adapter_fasta,
                quality_threshold=quality_threshold,
            )
        elif adapter_string is not None:
            cur_sample = FastpInputString(
                sample=sample,
                read_type=read_type,
                adapter_string=adapter_string,
                quality_threshold=quality_threshold,
            )
        else:
            cur_sample = FastpInput(
                sample=sample,
                read_type=read_type,
                quality_threshold=quality_threshold,
            )

        inputs.append(cur_sample)

    return inputs


@medium_task
def run_fastp(
    fastp_input: Union[FastpInputFASTA, FastpInputString, FastpInput],
) -> LatchDir:
    """Adapter removal and read trimming with fastp"""

    message(
        "info",
        {
            "title": "Set fastp mode",
            "info": f"Running fastp in {fastp_input.read_type}-end mode.",
        },
    )

    sample_name = fastp_input.sample.name
    output_dir = Path("fastp_results").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    output_prefix = f"{str(output_dir)}/{sample_name}"

    out1_name = (
        f"{output_prefix}.trim.fastq.gz"
        if fastp_input.read_type == "single"
        else f"{output_prefix}_1.trim.fastq.gz"
    )

    _fastp_cmd = [
        "/root/fastp",
        "--in1",
        fastp_input.sample.read1.local_path,
        "--out1",
        out1_name,
        "--json",
        f"{output_prefix}.fastp.json",
        "--html",
        f"{output_prefix}.fastp.html",
        "--thread",
        "16",
        "--qualified_quality_phred",
        str(fastp_input.quality_threshold),
    ]

    if fastp_input.read_type == "paired":
        _fastp_cmd.extend(
            [
                "--in2",
                fastp_input.sample.read2.local_path,
                "--out2",
                f"{output_prefix}_2.trim.fastq.gz",
            ]
        )

    # Handle adapter content
    if hasattr(fastp_input, "adapter_fasta"):
        _fastp_cmd.extend(["--adapter_fasta", fastp_input.adapter_fasta.local_path])
    elif hasattr(fastp_input, "adapter_string"):
        _fastp_cmd.extend(["--adapter_sequence", fastp_input.adapter_string])
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

        if fastp_input.read_type == "paired":
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
    paired_end: List[PairedEnd],
    quality_threshold: int = 30,
    adapter_fork: str = "none",
    adapter_fasta: Optional[LatchFile] = None,
    adapter_string: Optional[str] = None,
    single_end: Optional[List[SingleEnd]] = None,
) -> List[LatchDir]:
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
    fastp_inputs = organize_fastp_inputs(
        paired_end=paired_end,
        quality_threshold=quality_threshold,
        single_end=single_end,
        adapter_fasta=adapter_fasta,
        adapter_string=adapter_string,
    )

    return map_task(run_fastp)(fastp_input=fastp_inputs)


LaunchPlan(
    fastp,
    "Test Data",
    {
        "paired_end": [
            PairedEnd(
                name="SRR579291",
                read1=LatchFile("s3://latch-public/test-data/4318/SRR579291_1.fastq"),
                read2=LatchFile("s3://latch-public/test-data/4318/SRR579291_2.fastq"),
            ),
            PairedEnd(
                name="SRR579292",
                read1=LatchFile("s3://latch-public/test-data/4318/SRR579292_1.fastq"),
                read2=LatchFile("s3://latch-public/test-data/4318/SRR579292_2.fastq"),
            ),
        ],
        "quality_threshold": 30,
        "adapter_fasta": LatchFile(
            "s3://latch-public/test-data/4318/sample_adapters.fa"
        ),
    },
)
