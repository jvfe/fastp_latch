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
    "sample_fork": LatchParameter(),
    "paired_end": LatchParameter(
        display_name="Paired-end reads",
        description="FASTQ files",
        batch_table_column=True,
    ),
    "single_end": LatchParameter(
        display_name="Single-end reads",
        description="FASTQ files",
        batch_table_column=True,
    ),
    "quality_threshold": LatchParameter(
        display_name="Minimum quality", description="Phred quality score"
    ),
    "adapter_fork": LatchParameter(),
    "adapter_string": LatchParameter(display_name="Adapter sequence"),
    "adapter_fasta": LatchParameter(
        display_name="Adapter FASTA",
        detail="(.fa, .fna, .fasta)",
        rules=[
            LatchRule(regex="(.fa|.fna|.fasta)$", message="Must be a valid FASTA file")
        ],
    ),
    "output_directory": LatchParameter(
        display_name="Output directory",
    ),
}

FLOW = [
    Section(
        "Samples",
        Text(
            "Sample provided has to include an identifier for the sample (Sample name)"
            " and one or two files corresponding to the reads (single-end or paired-end, respectively)"
        ),
        Fork(
            "sample_fork",
            "Choose read type",
            paired_end=ForkBranch("Paired-end", Params("paired_end")),
            single_end=ForkBranch("Single-end", Params("single_end")),
        ),
        Text("Name of the output directory to send results to."),
        Params("output_directory"),
    ),
    Section(
        "Quality threshold",
        Text(
            "Select the quality value in which a base is qualified."
            "Quality value refers to a Phred quality score"
        ),
        Params("quality_threshold"),
    ),
    Section(
        "Adapter content",
        Text(
            "Trim adapter sequences provided below. Can either be a character sequence"
            " specifying the adapter or a FASTA file containing the adapter sequences."
            "Or, alternatively, you can let fastp automatically detect adapter sequences"
        ),
        Fork(
            "adapter_fork",
            "Use a character sequence or a FASTA file containing adapters",
            adapter_all=ForkBranch(
                "Detect adapters",
                Text("Let fastp automatically detect adapter content"),
            ),
            adapter_fasta=ForkBranch("Adapter FASTA", Params("adapter_fasta")),
            adapter_string=ForkBranch("Adapter sequence", Params("adapter_string")),
        ),
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
