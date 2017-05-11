#!/usr/bin/env python

import argparse
import re
import subprocess
import os.path

def ExistingFile(fileName):
	if os.path.isfile(fileName)==False:
		raise argparse.ArgumentTypeError("File not present")
	return fileName

def getPosLen(line):
	Pos_and_Len =[int(s) for s in line.split() if s.isdigit()]
	print(Pos_and_Len)
	Pos = Pos_and_Len[0]
	Len = Pos_and_Len[1]
	return Pos, Len



def combination(output_array):
	#parser = argparse.ArgumentParser(description = 'take the informations from the bin')
	#parser.add_argument('--combination',required = True, nargs='*',type = ExistingFile)
	#args = parser.parse_args()

	fout = open('mm.bin','wb')
	total_list=[]
	all_binname = []
	all_stream = []
	for i in range(len(output_array)):
		each_list = []
		bin_txt_name = str(output_array[i])
		#binname = (bin_txt_name.replace(".txt"," ")).strip()
		binname = bin_txt_name + ".bin"
		all_binname.append(binname)
		open_stream = open(binname,'r')
		all_stream.append(open_stream)
		txt_name = bin_txt_name +".txt"
		fnalu = open(txt_name,'r')
		while True:
			each_line = fnalu.readline()
			if each_line.strip() == '':
				break
			else:
				each_list.append(each_line)
		total_list.append(each_list)
	
	

	begin_index = 0
	
	now_flag = 0
	next_flag = 0
	active = 1
	print()
	while (active == 1):
		if (begin_index > len(total_list[0])-len(all_binname)-2):

			for m in range(len(all_binname)):
				begin_index = begin_index + 1
				Pos, Len = getPosLen(total_list[m][begin_index])
				all_stream[j].seek(Pos,0)
				fout.write(all_stream[m].read(Len))
			active = 0
		else:			
			for j in range(len(all_binname)):
				# get the string
				break_flag = 0
				
				if (now_flag + next_flag == 1):
					now_flag = 0
					next_flag = 0
					break
				else:
					begin_index = begin_index + 1
					Pos, Len = getPosLen(total_list[j][begin_index])

					# when we see the .txt for different bps, in the same line(each line represent a frame ), the type of this frame must be the same
					# for example , in the 2000.txt the third line is : NALU1@ 36 : sz: 74 type:33 (SPS)
					#               in the 2250.txt the third line is : NALU1@ 36 : sz: 74 type:33 (SPS)
					# if the 2250.txt is not in the type of 33, it means that it exist the erreur
					# the "if" below shows the condition when the frame is not a normal frame, like(VPS,SPS,PPS)
					if "CODED_SLICE" not in total_list[0][begin_index]:
						for x in range(1,len(output_array)):
							if "CODED_SLICE" in total_list[x][begin_index]:
								break_flag = 1
								print ("probleme exist")

						# the "if" below shows that the above do not execute, otherwise, break_flag = 0
						if break_flag == 0:  
							
							# if we find that this frame is not a normal frame , it means , for the other .txt, the context is the same 
							# for example , in the 2000.txt the third line is : NALU1@ 36 : sz: 74 type:33 (SPS)
							#               in the 2250.txt the third line is : NALU1@ 36 : sz: 74 type:33 (SPS)
							#  the context must be the same , so we just need to extrat the context in the first .txt
							all_stream[0].seek(Pos,0)
							#fout.write(bin(all_stream[0].read(Len))[2:].zfill(8))
							fout.write(all_stream[0].read(Len))
							'''
							for i in range(Len):
								stream = all_stream[0].read(1)
								fout.write(stream)
							'''
							# now_flag = 0 means that now we are in the innormal frame 
							# next_flag represent if it will change from innormal frame(VPS,PPS,SPS) to normal frame
							now_flag = 0
							next_flag = ("CODED_SLICE" in total_list[j][begin_index+1])
							
					else:
						# the next "for" deal with the same probleme of above
						for y in range(1,len(output_array)):
							if "CODED_SLICE" not in total_list[x][begin_index]:
								break_flag = 1
								print ("probleme exist")

						if break_flag == 0:
							all_stream[j].seek(Pos,0)
							#fout.write(bin(all_stream[j].read(Len))[2:].zfill(8))
							fout.write(all_stream[j].read(Len))
							'''
							for i in range(Len):
								stream = all_stream[j].read(1)
								
								fout.write(stream)
							'''
							# now_flag = 1 means that now we are in the normal frame
							now_flag = 1
							next_flag = ("CODED_SLICE" in total_list[j][begin_index+1])
				
			
				
			
		
	fout.close()
		
if __name__ == '__main__':
	combination()
	
