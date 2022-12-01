# filename: test.py
#
# Run this as below
#
# >>> run-script scripts/test.py

from latch.types import LatchFile

import wf
from wf.types import FastpInput, FastpInputFASTA, FastpInputString, PairedEnd, SingleEnd

wf.run_fastp(
    fastp_input=FastpInputFASTA(
        sample=PairedEnd(
            name="testSRR",
            read1=LatchFile("latch:///Crohn/SRR579292_1.fastq"),
            read2=LatchFile("latch:///Crohn/SRR579292_2.fastq"),
        ),
        quality_threshold=30,
        read_type="paired",
        output_directory="test_results",
        adapter_fasta=LatchFile("s3://latch-public/test-data/4318/sample_adapters.fa"),
    ),
)

wf.run_fastp(
    fastp_input=FastpInputString(
        sample=PairedEnd(
            name="testSRR",
            read1=LatchFile("latch:///Crohn/SRR579292_1.fastq"),
            read2=LatchFile("latch:///Crohn/SRR579292_2.fastq"),
        ),
        quality_threshold=30,
        read_type="paired",
        output_directory="test_results",
        adapter_string="AGATCGGAAGAGCACACGTCTGAACTCCAGTCA",
    ),
)


wf.run_fastp(
    fastp_input=FastpInput(
        sample=PairedEnd(
            name="testSRR",
            read1=LatchFile("latch:///Crohn/SRR579292_1.fastq"),
            read2=LatchFile("latch:///Crohn/SRR579292_2.fastq"),
        ),
        quality_threshold=30,
        read_type="paired",
        output_directory="test_results",
    ),
)

wf.run_fastp(
    fastp_input=FastpInput(
        sample=SingleEnd(
            name="testSRR_single",
            read1=LatchFile("latch:///Crohn/SRR579292_1.fastq"),
        ),
        quality_threshold=30,
        read_type="single",
        output_directory="test_results",
    ),
)
