import argparse
import os
import glob
import random
import shutil
import pprint


def normalize_dir_files(path, limit):
    for d in glob.glob(os.path.join(path, "*")):
        if not os.path.isdir(d):
            continue
        files = [f for f in glob.glob(os.path.join(d, "*"))
                 if os.path.isfile(f)]
        print "Dir %s has %d files" % (d , len(files))
        if len(files) > limit:
            print "Deleting %d files" % (len(files) - limit)
            random.shuffle(files)
            for f in files[limit:]:
                print "\tDeleting %s" % f
                os.unlink(f)

def word_count(path):
    count = 0
    with open(path) as f:
        for line in f:
            count += len(list(t for t in line.strip().split()
                              if t != ""))
    return count

def special_delete(file, words_threshold):
    words = open(file).read().strip().split()
    if len(words) < words_threshold * 3:
        print "WARNING: file %s has %s words, words_threshold=%s" % (file, len(words), words_threshold)
    start_words = words[:words_threshold]
    end_words = words[-words_threshold:]
    mid_point = len(words)/2
    mid_words = words[(mid_point - words_threshold/2):(mid_point + words_threshold)][:words_threshold]
    with open(file, "w") as f:
        f.write("\n".join(start_words + mid_words + end_words))

def normalize_dir_words(path, limit, file_threshold, words_threshold):
    for d in glob.glob(os.path.join(path, "*")):
        if not os.path.isdir(d):
            continue
        files = {f: word_count(f) for f in glob.glob(os.path.join(d, "*"))
                 if os.path.isfile(f)}
        print "Dir %s has %d words in files" % (d , sum(files.values()))
        print "Words count %s" % pprint.pformat(files)
        while True:
            total_words = sum(files.values())
            if total_words < limit:
                break
            to_delete = [(f,w) for f,w in files.iteritems()
                         if total_words - w >= limit]
            random.shuffle(to_delete)
            if to_delete != []:
                file, words = to_delete[0]
                print "Deleting file %s with %d words, remaining words %d" % (file, words, total_words - words)
                os.unlink(file)
                del files[file]
                continue

            to_special_delete = [(f,w) for f,w in files.iteritems()
                                 if w > file_threshold]
            random.shuffle(to_special_delete)
            if to_special_delete != []:
                file, words = to_special_delete[0]
                print "Special Deleting file %s with %d words, remaining words %d" % (file,
                                                                                      words,
                                                                                      total_words - words + 3 * words_threshold)
                special_delete(file, words_threshold)
                files[file] = word_count(file)
                continue

            break

def normalize_dir_words_truncate(path, file_threshold, words_threshold):
    for d in glob.glob(os.path.join(path, "*")):
        if not os.path.isdir(d):
            continue
        files = {f: word_count(f) for f in glob.glob(os.path.join(d, "*"))
                 if os.path.isfile(f)}
        for f, words in files.iteritems():
            if words > file_threshold:
                print "Truncating file %s with %d words" % (f, words)
                special_delete(f, words_threshold)
                print "\tremaining words %d" % word_count(f)



def normalize_dir(path, limit, use_files, use_words, truncate_files,
                  file_threshold, words_threshold):
    if use_files:
        normalize_dir_files(path, limit)
    elif use_words:
        normalize_dir_words(path, limit, file_threshold, words_threshold)
    elif truncate_files:
        normalize_dir_files(path, limit)
        normalize_dir_words_truncate(path, file_threshold, words_threshold)


def main():
    parser = argparse.ArgumentParser(description='Normilize files in directory')
    parser.add_argument('directories', metavar='DIR', type=str, nargs='+',
                        help='list of directories in which the normalization of files will be performed')
    parser.add_argument('--limit', metavar='X', type=int, required=True,
                        help='specify limit value X which is used for normalization process')
    parser.add_argument('--file-threshold', metavar='N', type=int, default=3000,
                        help='In files above size of N delete all except first mid and last M words')
    parser.add_argument('--words-threshold', metavar='M', type=int, default=1000,
                        help='In files above size of N delete all except first mid and last M words')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--files', action="store_true",
                       help='perform normalization using number of files')
    group.add_argument('--words', action="store_true",
                       help='perform normalization using number of words in files')
    group.add_argument('--truncate-files', action="store_true",
                       help='Normalize directories by number of files, and afterward, '
                            'find all files over N words and keep first, middle, and '
                            'last M words in the document')


    args = parser.parse_args()
    print args

    random.seed()

    for d in args.directories:
        if not os.path.isdir(d):
            print "WARNING %s is not a directory" % d
            continue
        normalize_dir(d, args.limit, use_files=args.files, use_words=args.words,
                      truncate_files=args.truncate_files,
                      file_threshold=args.file_threshold,
                      words_threshold=args.words_threshold)

if __name__ == '__main__':
    main()