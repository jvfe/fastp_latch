from latch.types.metadata import (
    Fork,
    ForkBranch,
    LatchAuthor,
    LatchMetadata,
    LatchParameter,
    LatchRule,
    Params,
    Section,
    Spoiler,
    Text,
)

PARAMS = {
    "sample": LatchParameter(
        display_name="Sample",
        description="FASTQ files",
        batch_table_column=True,
    ),
}

FLOW = [
    Section(
        "Samples",
        Text(
            "Sample provided has to include an identifier for the sample (Sample name)"
            " and one or two files corresponding to the reads (single-end or paired-end, respectively)"
        ),
        Params("sample"),
    ),
]

fastp_docs = LatchMetadata(
    display_name="fastp - Low-quality sequence and adapter removal",
    documentation="https://github.com/jvfe/fastp_latch/blob/main/README.md",
    author=LatchAuthor(
        name="jvfe",
        github="https://github.com/jvfe",
    ),
    repository="https://github.com/jvfe/fastp_latch",
    license="MIT",
    parameters=PARAMS,
    tags=["pre-processing", "qc", "trimming"],
    flow=FLOW,
)