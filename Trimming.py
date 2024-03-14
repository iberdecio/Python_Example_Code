from Bio import SeqIO

def trim_sequences(input_file, output_file, start, end):

    with open(output_file, "w") as output_handle:
        for record in SeqIO.parse(input_file, "fasta"):
            trimmed_seq = record.seq[start-1:end]
            record.seq = trimmed_seq
            SeqIO.write(record, output_handle, "fasta")

input_file = "3to6.fasta"
output_file = "DeltaTrimmed_FullLength200.fasta"
start_coordinate = 21563
end_coordinate = 25384
trim_sequences(input_file, output_file, start_coordinate, end_coordinate)