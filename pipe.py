import argparse
import subprocess

def run_command(command):
    """Run a shell command and handle any errors."""
    result = subprocess.run(command, shell=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr.decode()}")
    else:
        print(f"Command Successful: {command}")
    return result.stdout.decode()

def calculate_average_qual(vcf_file):
    """Calculate average variant QUAL scores from a VCF file"""
    total_qual = 0
    count = 0

    with open(vcf_file, 'r') as file:
        for line in file:
            if line.startswith("#"):
                continue
            columns = line.strip().split("\t")
            qual = float(columns[5])
            total_qual += qual
            count += 1

    average_qual = total_qual / count if count > 0 else 0
    print(f"average qual: {average_qual}")
    return average_qual

def main():
    """Parse args, runs pipe, calculate the average qual scores"""

    # Dependency check warning
    print("WARNING: This script requires 'bwa', 'samtools', and 'bcftools' to be installed not installing these will not allow the script to be run correctly and will result in empty files")
    print("Please make sure all dependencies are installed before proceeding.\n")

    parser = argparse.ArgumentParser(description="BWA alignment and variant calling pipeline")
    parser.add_argument("sample_name", help="Common name of files (without _1.fq.gz or _2.fq.gz)")
    parser.add_argument("--bwa_ref", required=True, help="Path to the BWA reference genome file")
    parser.add_argument("--sam_ref", required=True, help="Path to the SAM reference genome file for bcftools")
    args = parser.parse_args()

    # Use the reference file paths from the command-line arguments
    bwa_ref = args.bwa_ref
    sam_ref = args.sam_ref

    sample_name = args.sample_name
    fastq1 = f"{sample_name}_1.fq.gz"
    fastq2 = f"{sample_name}_2.fq.gz"
    sam_file = f"{sample_name}.sam"
    sorted_sam = f"{sample_name}_s.sam"
    vcf_file = f"{sample_name}.vcf"

    print(f"Aligning {fastq1} and {fastq2} with {bwa_ref} to produce {sam_file}")
    bwa_command = f"bwa mem {bwa_ref} {fastq1} {fastq2} > {sam_file}"
    run_command(bwa_command)

    print(f"Sorting {sam_file} for input to bcftools")
    sort_command = f"samtools sort {sam_file} > {sorted_sam}"
    run_command(sort_command)

    print(f"Processing {sorted_sam} for variant calling with bcftools")
    bcftools_mpileup = f"bcftools mpileup -Ou -f {sam_ref} {sorted_sam} | bcftools call -mv -Ov -o {vcf_file}"
    run_command(bcftools_mpileup)

    print("Pipeline executed successfully. Output files:")
    print(f" Sorted SAM file: {sorted_sam}")
    print(f" Variant calling file: {vcf_file}")

    print("Calculate average Qual scores")
    calculate_average_qual(vcf_file)

if __name__ == "__main__":
    main()
