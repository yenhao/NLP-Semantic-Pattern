import sys, fileinput

def get_new_pattern():
    with open('new_pat_test.txt') as newpat:
        dict_new_pat = { line.strip().split('\t')[0]:line.strip().split('\t')[1] for line in newpat.readlines() }
    return dict_new_pat

if __name__ == '__main__':
	dict_new_pat = get_new_pattern()
	for line in fileinput.input():
		line_list = line.split('\t')
		if 'something' in line_list[1].split():
			if line_list[1] in dict_new_pat:
				line_list[1] = dict_new_pat[line_list[1]]
				
				# print line_list[1]
				print '\t'.join(line_list).strip()
			else:
				print line.strip()
		else :
			print line.strip()
			# print 'XD'