#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--bed_file", type=str, help="Path to the BED file")
parser.add_argument("--junction_file", type=str, help="Path to the junction file")
parser.add_argument("--result_file", type=str, help="Path to the result file")
args = parser.parse_args()

# Open the files based on the provided paths
bed_file = open(args.bed_file)
junction_file = open(args.junction_file)
result_file = open(args.result_file, "w")

report_genes = ["MET", "EGFR"]
FP_exon = ["EGFR_ENST00000455089.5_exon_23", "MET_ENST00000318493.1_exon_4"]

gene_dict = {}
pos_dict = {}


for line in bed_file:
    """
    
    This chunk of code reads the bed file and creates a two dictionary element of 
    the genes and their corresponding chromosome postions

    """
    
    lline = line.strip().split("\t")
    chrom = lline[0]
    start_pos = int(lline[1])
    end_pos = int(lline[2])+1
    key1 = chrom + "_" + str(start_pos)
    key2 = chrom + "_" + str(end_pos)
    region = lline[3]
    gene = region.split("_")[0]
    
    if gene not in report_genes:
        continue
    
    exon = "0"
    if region.find("exon") != -1:
        exon = region.split("_exon_")[1]
    elif len(exon.split("part")) > 1:
        exon = int(exon.split("part")[0])
    exon = int(exon)

    if gene not in gene_dict:
        gene_dict[gene] = []
    
    gene_dict[gene].append([chrom, start_pos, end_pos, exon, region])
    pos_dict[key1] = gene
    pos_dict[key2] = gene


##print (gene_dict)
## print (pos_dict)
## Normal junctions are the ones 
normal_junction = {}
unnormal_junction = {}


for line in junction_file:
    lline = line.strip().split("\t")
    chrom = "chr" + str(lline[0])
    start_pos = int(lline[1])
    end_pos = int(lline[2])
    nr_reads = int(lline[6])
    key1 = chrom + "_" + str(start_pos)
    key2 = chrom + "_" + str(end_pos)

    if key1 not in pos_dict:
        continue

    i_start = 100
    i_end = 100
    i_start_name = ""
    i_end_name = ""

    for exon in gene_dict[pos_dict[key1]]:

        if exon[2] == start_pos:
            i_start = exon[3]
            i_start_name = exon[4]

        if exon[1] == end_pos:
            i_end = exon[3]
            i_end_name = exon[4]

    if i_end == 100:
        for exon in gene_dict[pos_dict[key1]]:
            if abs(exon[1] - end_pos) < 100:
                i_end = exon[3]
                i_end_name = exon[4]

    if i_end - i_start > 1 or i_start == 100 or i_end == 100:
        if nr_reads >= 5:
            if key1 in unnormal_junction:
                if nr_reads > unnormal_junction[key1][0]:
                    unnormal_junction[key1] = [nr_reads, i_start, i_end, key2, i_start_name, i_end_name]
            else:
                unnormal_junction[key1] = [nr_reads, i_start, i_end, key2, i_start_name, i_end_name]

    if key1 in normal_junction:
        normal_junction[key1].append([nr_reads, i_start, i_end, key2, i_start_name, i_end_name])
    else:
        normal_junction[key1] = [[nr_reads, i_start, i_end, key2, i_start_name, i_end_name]]

#print (normal_junction)
print (unnormal_junction)


result_file.write("Gene\tleft_break\tright_break\tstart_exon\tend_exon\tsupporting_reads\treads_supporting_normal_splicing\tfraction_skipped_reads\tconfidence\teffect\n")

for unnormal_key in unnormal_junction:
    gene = pos_dict[unnormal_key]
    nr_unnormal_reads = unnormal_junction[unnormal_key][0]
    nr_normal_reads = 0
    if unnormal_key in normal_junction:
        normal_junction[unnormal_key].sort(reverse=True)
        if normal_junction[unnormal_key][0][0] == nr_unnormal_reads:
            if len(normal_junction[unnormal_key]) > 1:
                nr_normal_reads = normal_junction[unnormal_key][1][0]
        else:
            nr_normal_reads = normal_junction[unnormal_key][0][0]
    i_start = unnormal_junction[unnormal_key][1]
    i_end = unnormal_junction[unnormal_key][2]
    start_exon = ""
    end_exon = ""
    start_exon_name = ""
    end_exon_name = ""

    if i_start != 100:
        start_exon = str(i_start)
        start_exon_name = str(unnormal_junction[unnormal_key][4])
        print (normal_junction[unnormal_key])
        start_exon_position = int(unnormal_key.split("_")[1])-1
        print (start_exon_position)
    else:
        start_exon = unnormal_key
        start_exon_position = int(unnormal_key.split("_")[1])-1
    
    if i_end != 100:
        end_exon = str(i_end)
        end_exon_name = str(unnormal_junction[unnormal_key][5])
        end_exon_position = int(unnormal_junction[unnormal_key][3].split("_")[1])+1

        print (end_exon_position)
    else:
        continue

    fraction_skipped_reads = nr_unnormal_reads / float(nr_unnormal_reads + nr_normal_reads)
    gene_left_exon = str(gene) + "_" + "exon" + "_" + str(start_exon_name.split("_")[-1])
    gene_right_exon = str(gene) + "_" + "exon" + "_" + str(end_exon_name.split("_")[-1])

    left_break = unnormal_key.split("_")[0]+":"+str(start_exon_position)
    right_break = unnormal_key.split("_")[0]+":"+str(end_exon_position)
    confidence = 'high' if fraction_skipped_reads >= 0.80 else 'medium' if fraction_skipped_reads >= 0.30 else 'low'

    if fraction_skipped_reads > 0.1 and nr_unnormal_reads > 100 and end_exon_name not in FP_exon:
        result_file.write(
            gene + "\t" + left_break + "\t" + right_break +"\t" + gene_left_exon + "\t" + gene_right_exon + "\t" + str(nr_unnormal_reads) + "\t" + str(nr_normal_reads) + "\t" + str(fraction_skipped_reads) + "\t" + str(confidence)+","+"mitelman" + "\t" +"in-frame"+ "\n"
        )


result_file.close()

