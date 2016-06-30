PROGRAM FLOW
============

The program execution is divided into two parts. First part computes the collocation frequency and individual frequencies. The second part computes the t-score and mi-scores.

Freq_col_calc.py [refer freq_input.txt for a sample set of values]
================
The program expects the following console inputs.
===Enter corpus path=== [Given a folder path, it takes all text files from it and its subfolders]
===Collocation within sentence or across a text (1/0)=== [Should collocations be done within sentence or across sentences]
===Do you want the collocation to be directional or non-directional (1/0)===
	eg: word1 word2 word3 word4 word5.
	directional::  If word3 is considered and left and right sizes are 2, then the collocation pairs will be word3-word1, word3-word2, word3-word4, word3-word5.
	undirectional:: If word3 is considered and left and right sizes are 2,then the collocation pairs will be word1-word3, word2-word3, word3-word4, word3-word5.
					In this case, pairings are always done in the order in which the words are present.
===Enter left size=== [words that are present left to the current word that are considered for collocation]
===Enter right size=== [words that are present right to the current word that are considered for collocation]
===Enter the number of parallel threads to run=== [If the corpus is huge the texts are divided into equal parts and are processed in parallel. The frequencies are then combined by the parent process]

Output files (collocations.csv and ind_freqency.csv) are stored in the current working directory.

score_calc_cb.py [refer input_cb.txt for a sample set of values]
================
The program expects the following console inputs.
===Enter collocations file path:=== [path of output from Freq_col_calc.py program]
===Enter Individual Frequencies file path:=== [path of output from Freq_col_calc.py program]
===Enter codebook list file path:=== [path of file containing the list of words to be considered while calculating scores]
===Do you need both words of the pairing to be present in codebook (1/0)=== [should a pairing be considered if both or either of the words are present in codebook]
===Do you need a cutoff for t_score value (y/n):=== [t_score cutoff indicator]
===Enter t_score cutoff:=== [t_score cutoff value. optional input based on previous value]
===Do you need a cutoff for mi_score value (y/n):=== [mi_score cutoff indicator]
===Enter mi_score cutoff:=== [mi_score cutoff value. optional input based on previous value]
===Enter file path for t_score output:=== [path for t_score output]
===Enter file path for mi_score output:=== [path for mi_score output]

score_calc_swl.py [refer input_swl.txt for a sample set of values]
================
The program expects the following console inputs.
===Enter collocations file path:=== [path of output from Freq_col_calc.py program]
===Enter Individual Frequencies file path:=== [path of output from Freq_col_calc.py program]
===Enter stop word list file path:=== [path of file containing the list of words that won't be considered while calculating scores]
===Do you need a cutoff for t_score value (y/n):=== [t_score cutoff indicator]
===Enter t_score cutoff:=== [t_score cutoff value. optional input based on previous value]
===Do you need a cutoff for mi_score value (y/n):=== [mi_score cutoff indicator]
===Enter mi_score cutoff:=== [mi_score cutoff value. optional input based on previous value]
===Enter file path for t_score output:=== [path for t_score output]
===Enter file path for mi_score output:=== [path for mi_score output]

run.sh
======
Script that runs the three programs by redirecting values from the corresponding input text files to its execution.
