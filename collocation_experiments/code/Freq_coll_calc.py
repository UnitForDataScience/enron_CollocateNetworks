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

# Gets the list of all folders (recursively) that are present under the given folder
def get_folders(sub_folder):
	folders = []
	for fil in os.listdir(sub_folder):
		if os.path.isdir(sub_folder+'/'+fil):
			folders.append(sub_folder+'/'+fil)
			folders += get_folders(sub_folder+'/'+fil)
	return folders

# Gets the list of files (ending with .txt) that are present directly under the given folder
def dir_function(sub_folder):
	files = []
	for fil in os.listdir(sub_folder):
		if fil.endswith(".txt"):
			files.append(sub_folder+'/'+fil)
	return files

# Gets the recursive list of all subfolders present within the given folder.
# Iterates through the list and gets all the text files contained within it.
def dir_functionV1(sub_folder):
	folders = []
	files = []
	folders.append(sub_folder)
	folders += get_folders(sub_folder)
	for folder in folders:
		files += dir_function(folder)
	return files

# Used to consider ordering of the pair.
# Either it outputs in the given order or sorts in ascending order and returns the pair.
def get_key(input1, input2,dir_indicator):
	if dir_indicator == 1:
		return input1+'-'+input2
	else:
		if input1>input2:
			return input2+'-'+input1
		else:
			return input1+'-'+input2

# Finds collocation for the ordered word list given by pairing in order word-left and word-right.
def find_collocation_dir(word_list, left_size, right_size, ind_counter, cnt):
	wll = len(word_list)
	if wll <= right_size+1:
		for i in range (wll):
			ind_counter[word_list[i].lower()]+=1
			for j in range (0,i):
				cnt[get_key(word_list[j].lower(),word_list[i].lower(),1)]+=1
	else:
		for i in range (right_size+1):
			ind_counter[word_list[i].lower()]+=1
			for j in range (0,i):
				cnt[get_key(word_list[j].lower(),word_list[i].lower(),1)]+=1
		for i in range (right_size+1,wll):
			ind_counter[word_list[i].lower()]+=1
			for j in range (i-right_size,i):
				cnt[get_key(word_list[j].lower(),word_list[i].lower(),1)]+=1
	if wll <= left_size+1:
		for i in range (wll):
			for j in range (0,i):
				cnt[get_key(word_list[i].lower(),word_list[j].lower(),1)]+=1
	else:
		for i in range (left_size+1):
			for j in range (0,i):
				cnt[get_key(word_list[i].lower(),word_list[j].lower(),1)]+=1
		for i in range (left_size+1,wll):
			for j in range (i-left_size,i):
				cnt[get_key(word_list[i].lower(),word_list[j].lower(),1)]+=1

# Finds collocation for the ordered word list given by pairing them in the order in which they arrive.
# But word1 - word2 and word2 - word1 will still be taken as separate pairs.
def find_collocation_undir(word_list, window_size, ind_counter, cnt):
	wll = len(word_list)
	if wll <= window_size:
		for i in range (wll):
			ind_counter[word_list[i].lower()]+=1
			for j in range (0,i):
				cnt[get_key(word_list[j].lower(),word_list[i].lower(),1)]+=1
	else:
		for i in range (window_size):
			ind_counter[word_list[i].lower()]+=1
			for j in range (0,i):
				cnt[get_key(word_list[j].lower(),word_list[i].lower(),1)]+=1
		for i in range (window_size,wll):
			ind_counter[word_list[i].lower()]+=1
			for j in range (i-window_size+1,i):
				cnt[get_key(word_list[j].lower(),word_list[i].lower(),1)]+=1

# Word tokenizes the sentence or the entire text based on an indicator
# calls collocation function based on left-size and right-size
def process_textV1(data, sent_indicator, left_size, right_size, ind_counter, cnt):
	if sent_indicator == 1:
		sentences = sent_tokenize(data)
		for sentence in sentences:
			sentence = re.sub("[^A-Za-z0-9' ]+",' ',sentence)
			sentence = re.sub(' +',' ',sentence)
			word_list = word_tokenize(sentence)
			find_collocation_dir(word_list,left_size,right_size,ind_counter, cnt)
	else:
		data = re.sub("[^A-Za-z0-9' ]+",' ',data)
		data = re.sub(' +',' ',data)
		word_list = word_tokenize(data)
		find_collocation_dir(word_list,left_size,right_size,ind_counter, cnt)

# Word tokenizes the sentence or the entire text based on an indicator
# calls collocation function based on window size (usually left_size + right_size +1)
def process_text(data, sent_indicator, window_size, ind_counter,dir_indicator, cnt):
	if sent_indicator == 1:
		sentences = sent_tokenize(data)
		for sentence in sentences:
			sentence = re.sub("[^A-Za-z0-9' ]+",' ',sentence)
			sentence = re.sub(' +',' ',sentence)
			word_list = word_tokenize(sentence)
			find_collocation_undir(word_list,window_size,ind_counter, cnt)
	else:
		data = re.sub("[^A-Za-z0-9' ]+",' ',data)
		data = re.sub(' +',' ',data)
		word_list = word_tokenize(data)
		find_collocation_undir(word_list,window_size,ind_counter,cnt)

# The contents are read from file and all special characters and punctuations are removed.
def pre_process_text(filename, ind_counter, cnt, sent_ind,dir_indicator, window_size, left_size, right_size):
	data = ''
	with open(filename,'r') as f:
		for line in f.readlines():
			line = line.replace('\r\n',' ')
			data = data +line
		data = re.sub("[^A-Za-z0-9'_. ]+",' ',data)
		data = re.sub(' +',' ',data)
		if dir_indicator == 1:
			process_textV1(data, sent_ind, left_size, right_size, ind_counter, cnt)
		else:
			process_text(data,sent_ind,window_size, ind_counter,dir_indicator, cnt)

#file list iterator. And it is the starting point of the process
def process_starter(dir_list, sent_ind,dir_indicator, window_size, left_size, right_size ,q):
	ind_counter = Counter()
	cnt = Counter()
	print 'File list size: '+str(len(dir_list))
	for filename in dir_list:
		pre_process_text(filename, ind_counter, cnt, sent_ind,dir_indicator, window_size, left_size, right_size)
	print str(len(ind_counter))+'    '+str(len(cnt))
	result = {'IND_LIST':ind_counter, 'COL_LIST':cnt}
	q.put(result)
	print 'result put in queue'

def main_process(dir_path,sent_ind,dir_indicator,window_size,left_size,right_size,no_threads):
	ind_counter = Counter()
	cnt = Counter()
	q = Queue()
	dir_list = dir_functionV1(dir_path)
	length = len(dir_list)
	threads = []
	if length == 0:
		return 1
	elif length < no_threads:
		print 'inside here'
		p1 = Process(target = process_starter, args=(dir_list, sent_ind,dir_indicator,window_size,left_size, right_size,q,))
		p1.start()
		temp = q.get()
		for key, value in temp['IND_LIST'].most_common():
			ind_counter[key] += value
		for key, value in temp['COL_LIST'].most_common():
			cnt[key] += value
		p1.join()
	else:
		step_fn = int(floor(len(dir_list)/no_threads))
		print step_fn
		for i in range (0,no_threads):
			if i == 0:
				p = Process(target = process_starter, args=(dir_list[:step_fn], sent_ind,dir_indicator,window_size,left_size, right_size,q,))
			elif i == no_threads -1:
				p = Process(target = process_starter, args=(dir_list[i*step_fn:], sent_ind,dir_indicator,window_size,left_size, right_size,q,))
			else:
				p = Process(target = process_starter, args=(dir_list[i*step_fn:(i+1)*step_fn], sent_ind,dir_indicator,window_size,left_size, right_size,q,))
			threads.append(p)
		for thread in threads:
			thread.start()
		for i in range (0,no_threads):
			temp = q.get()
			for key, value in temp['IND_LIST'].most_common():
				ind_counter[key] += value
			for key, value in temp['COL_LIST'].most_common():
				cnt[key] += value
		for thread in threads:
			thread.join()
	print 'frequency calculation complete. Writing out frequency results in ind_frequency.csv and coallocations.csv'
	with open('ind_frequency.csv','w') as f1:
		for key, value in ind_counter.most_common():
			f1.write(key+','+str(value)+'\n')
	with open('collocations.csv','w') as f2:
		for key, value, in cnt.most_common():
			tokens = key.split('-')
			f2.write(tokens[0]+','+tokens[1]+','+str(value)+'\n')
	print 'Writing to file complete!'
	return 0

def init():
	left_size = 0
	right_size = 0
	window_size = 0
	path = raw_input('Enter corpus path\n')
	sent_ind = int(raw_input('Collocation within sentence or across a text (1/0)\n'))
	dir_indicator = int(raw_input('Do you want the collocation to be directional or non-directional (1/0)\n'))
	left_size = int(raw_input('Enter left size\n'))
	right_size = int(raw_input('Enter right size\n'))
	if not dir_indicator == 1:
		window_size = left_size+right_size+1
	thread_no = int(raw_input('Enter the number of parallel threads to run\n'))
	print 'Window Size: '+str(window_size)
	start_ts = time()
	main_process(path,sent_ind,dir_indicator,window_size,left_size,right_size,thread_no)
	time_taken = divmod((time()-start_ts),60)
	print("Overall time taken for frequency calculation: %d minutes and %d seconds" %(time_taken[0],time_taken[1]))

if __name__ == '__main__':
	#/home/anandh/Documents/ScienceFiction-master/Coallocations/texts
	#/home/anandh/Documents/ScienceFiction-master/textProcessed
	#/home/anandh/Documents/ScienceFiction-master/mbyearwise/2006
	#main_process(dir_path,sent_ind,dir_indicator,window_size,no_threads)
	#main_process('/home/anandh/Documents/ScienceFiction-master/Coallocations/texts',int(sent_ind),int(dir_indicator),int(window_size),left_size,right_size,int(thread_no))
	init()
