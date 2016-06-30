#!/usr/bin/python2.7
from __future__ import division
from multiprocessing import Process, Queue
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize
from collections import Counter
from math import floor, sqrt, log
from time import time
from sys import argv
import Queue as que
import re
import os
import sys

sw_list = []
ind_list = Counter()
cnt = Counter()
cnt_counter = 0
ind_counter = 0
N=0

#input file paths
collocation_file = ""
ind_frequency_file = ""
stop_word_file = ""
t_score_output_file = ''
mi_score_output_file = ''
ts_cutoff_indicator = 0
mi_cutoff_indicator = 0
ts_cutoff = 0.0
mi_cutoff = 0.0

def isNumber(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

def load_values():
	global cnt_counter, ind_counter, sw_list,ind_list,cnt,N
	print 'loading frequencies and stopword list'
	with open(collocation_file,'r') as f:
		for line in f.readlines():
			tokens = line.split(',')
			cnt[tokens[0]+'-'+tokens[1]]+=int(tokens[2])
			cnt_counter+=1
	print 'reading collocations complete. Total count: '+str(cnt_counter)
	with open(ind_frequency_file,'r') as f:
		for line in f.readlines():
			tokens = line.split(',')
			val = int(tokens[1])
			ind_list[tokens[0]]+=val
			N+=val
			ind_counter+=1
	print 'reading individual frequencies complete.. Total count: '+str(ind_counter)+' value of N is '+str(N)
	with open(stop_word_file,'r') as f:
		for line in f.readlines():
			sw_list.append(line.strip().lower())
	print 'reading stopword list complete. Total count: '+str(len(sw_list))

def scoreCal():
	t_score = Counter()
	count = 0
	new_count = 0
	sys.stdout.write("Computing t_score: %.2f%% complete\r"%float(count*100.0/cnt_counter))
	sys.stdout.flush()
	cnt_items = cnt.items()
	for key, value in cnt_items:
		count+=1
		sys.stdout.write("Computing t_score: %.2f%% complete\r"%float(count*100.0/cnt_counter))
		sys.stdout.flush()
		words = key.split('-')
		if words[0].strip().lower() in sw_list or words[1].strip().lower() in sw_list:
			continue
		elif isNumber(words[0]) or isNumber(words[1]):
			continue
		fl = ind_list[words[0]]
		fr = ind_list[words[1]]
		den = sqrt(value)
		inter = float((fl*fr)/N)
		num = float(value - inter)
		res = float(num/den)
		if ts_cutoff_indicator == 1 and res < ts_cutoff:
			continue
		t_score[key] = res
		new_count +=1
	print ''
	count =0
	sys.stdout.write("Writing to t_score.csv: %.2f%% complete\r"%float(count*100.0/new_count))
	sys.stdout.flush()
	with open(t_score_output_file,'w') as f:
		f.write('source,target,t_score\n')
		for key, value in t_score.most_common():
			words = key.split('-')
			f.write(words[0]+','+words[1]+','+str(value)+'\n')
			count +=1
			sys.stdout.write("Writing to t_score.csv: %.2f%% complete\r"%float(count*100.0/new_count))
			sys.stdout.flush()
			del t_score[key]
	print ''
	mi = Counter()
	count = 0
	new_count = 0
	sys.stdout.write("Computing MI score: %.2f%% complete\r"%float(count*100.0/cnt_counter))
	sys.stdout.flush()
	for key, value in cnt_items:
		count+=1
		sys.stdout.write("Computing MI score: %.2f%% complete\r"%float(count*100.0/cnt_counter))
		sys.stdout.flush()
		words = key.split('-')
		if words[0].strip().lower() in sw_list or words[1].strip().lower() in sw_list:
			continue
		elif isNumber(words[0]) or isNumber(words[1]):
			continue
		fl = ind_list[words[0]]
		fr = ind_list[words[1]]
		den = sqrt(value)
		inter = float((fl*fr)/N)
		res = float(log(float(value/inter), 2))
		if mi_cutoff_indicator == 1 and res < mi_cutoff:
			continue
		mi[key] = res
		new_count+=1
	print ''
	count =0
	sys.stdout.write("Writing to mi.csv: %.2f%% complete\r"%float(count*100.0/new_count))
	sys.stdout.flush()
	with open(mi_score_output_file,'w') as f:
		f.write('source,target,mi_score\n')
		for key, value in mi.most_common():
			words = key.split('-')
			f.write(words[0]+','+words[1]+','+str(value)+'\n')
			count +=1
			sys.stdout.write("Writing to mi.csv: %.2f%% complete\r"%float(count*100.0/new_count))
			sys.stdout.flush()
			del mi[key]
	print ''

def init():
	global collocation_file, ind_frequency_file, stop_word_file, ts_cutoff_indicator, mi_cutoff_indicator, ts_cutoff, mi_cutoff, t_score_output_file, mi_score_output_file
	collocation_file = raw_input('Enter collocations file path:\n')
	ind_frequency_file = raw_input('Enter Individual Frequencies file path:\n')
	stop_word_file = raw_input('Enter stop word list file path:\n')
	temp1 = raw_input('Do you need a cutoff for t_score value (y/n):\n')
	if temp1 == 'y':
		ts_cutoff_indicator = 1
		ts_cutoff = float(raw_input('Enter t_score cutoff:\n'))
	temp1 = raw_input('Do you need a cutoff for mi_score value (y/n):\n')
	if temp1 == 'y':
		mi_cutoff_indicator = 1
		mi_cutoff = float(raw_input('Enter mi_score cutoff:\n'))
	t_score_output_file = raw_input('Enter file path for t_score output:\n')
	mi_score_output_file = raw_input('Enter file path for mi_score output:\n')
	start_ts = time()
	load_values()
	scoreCal()
	time_taken = divmod((time()-start_ts),60)
	print("Overall time taken for T-score and MI-score Calculation: %d minutes and %d seconds" %(time_taken[0],time_taken[1]))

if __name__ == '__main__':
	init()
