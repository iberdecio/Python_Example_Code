from Bio import SeqIO
import csv

def load_protein_sequence(fasta_file):
    for record in SeqIO.parse(fasta_file, "fasta"):
        return str(record.seq)

def load_negatively_selected_positions(csv_file):
    site_column_name = "Site"
    positions = []
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            positions.append(int(row[site_column_name]))
    return positions

def get_matches(start_position, end_position, target_positions):
    matches = []
    # Update to handle a 12-mer window
    for amino_acid_position in range(start_position, end_position - 11):  # Adjusted for a 12-mer window
        # Ensure the range is for 12 amino acids
        matching_positions = [pos for pos in range(amino_acid_position, amino_acid_position + 12) if pos in target_positions]
        # Check for at least 3 matches
        if len(matching_positions) >= 3:
            matches.append((amino_acid_position, matching_positions))
    return matches

def main():
    protein_sequence = load_protein_sequence("protein_omicron.fasta")
    negatively_selected_positions = load_negatively_selected_positions("(-) Omicron Sites.csv")

    output_file_path = "12mersOutfile.csv"  
    with open(output_file_path, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Epitope", "Matches"])  # Column headers
        # Adjust for a 12-mer window in the main loop
        for start_position in range(len(protein_sequence) - 11):  # Adjusted for a 12-mer window
            end_position = start_position + 12  # Adjusted for a 12-mer window
            matches = get_matches(start_position, end_position, negatively_selected_positions)
            if matches:
                epitope_sequence = protein_sequence[start_position:end_position]
                marked_sequence = list(epitope_sequence)
                for _, matching_positions in matches:
                    for pos in matching_positions:
                        # Ensure the position is within the current window
                        if pos - start_position < len(marked_sequence):  # Boundary check
                            marked_sequence[pos - start_position] = protein_sequence[pos].upper()  
                marked_epitope_sequence = "".join(marked_sequence)
                writer.writerow([marked_epitope_sequence, matches])  # Write to CSV
                print(f"Writing: Epitope: {marked_epitope_sequence}, Matches: {matches}")

if __name__ == "__main__":
    main()