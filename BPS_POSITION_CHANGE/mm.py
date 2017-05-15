#!/usr/bin/env python

import argparse
import re
import subprocess
import os.path



def readData(filename):
	good_quality = []
	bad_quality = []
	GOP_list = []
	file_data = open(filename,'r')
	col_in_list = [int(s) for s in file_data.readline().split() if s.isdigit()]
	row_in_list = [int(s) for s in file_data.readline().split() if s.isdigit()]
	total_frame_in_list = [int(s) for s in file_data.readline().split() if s.isdigit()]
	for each_line in file_data.readlines():
		if each_line.strip() != '':
			frame_good_bad = [int(s) for s in each_line.split() if s.isdigit()]
			print (frame_good_bad)
			GOP_list.append(frame_good_bad[0])
			good_quality.append(frame_good_bad[1])
			bad_quality.append(frame_good_bad[2])
	col = col_in_list[0]
	row = row_in_list[0]
	total_frame = total_frame_in_list[0]
	return col,row,total_frame,GOP_list,good_quality,bad_quality

# This function is used to find the GOP and save the position in a list
def FindGOP(filename):
	file_data = open(filename,'r')
	postion = 1
	GOP_position = []
	for each_line in file_data.readlines():
		if ("type:32 (VPS)" in each_line):
			GOP_position.append(postion)
		postion +=1
	return GOP_position
		
	
	

def ExistingFile(fileName):
	if os.path.isfile(fileName)==False:
		raise argparse.ArgumentTypeError("File not present")
	return fileName

def getPosLen(line):
	Pos_and_Len =[int(s) for s in line.split() if s.isdigit()]
	Pos = Pos_and_Len[0]
	Len = Pos_and_Len[1]
	return Pos, Len

# This function is used to put the seperate stream in the final stream
def composition(fout,index_in_GOP_list, GOP_list,GOP_postion,col,row,good_quality,bad_quality,begin_index):
	# find the begin line index in the text
	# for example GOP_position = [2,158,449,730,1047]
	#             GOP_list = [2,1,3]
	# the begin_line_index is the index of the beginning line in the relative .txt
	# we need to define the endline
	fullfill_end_flag = False
	begin_line_index_in_GOP_list = 0
	can_begin_flag = True
	for i in range(index_in_GOP_list):
		begin_line_index_in_GOP_list +=GOP_list[i]
		# very ofen ,we must identify if we can continue to codage because we must be sure that the beginning index of GOP_list is less than the total number of GOP
		if begin_line_index_in_GOP_list > len(GOP_position)-1:
			can_begin_flag = False
				
	
	if can_begin_flag :
		# begin to form the outputarray for this periode
		# in the output array, the index in the GOP_list represente the postion of good quality
		# for example: GOP_list = [2,1,3]  
		# the context in parameter.txt is  :
		#GOP, good quality, bad quality: 2 3000 1000
		#GOP, good quality, bad quality: 1 4500 2500
		#GOP, good quality, bad quality: 3 2500 1500
		# take split of 2x2 as example : the first 2 frames  output_array = [3000,1000,1000,1000]
		#                                the next 1 frames output_array = [2500,4500,2500,2500]   
		#                                the next 3 frames output_array = [1500,1500,2500,1500] 
		good_bps = good_quality[index_in_GOP_list]
		bad_bps = bad_quality[index_in_GOP_list]
		output_array = []
		num_bps = (col+1)*(row+1)
		all_binname = []
		all_stream = []
		total_list=[] 
		for j in range(num_bps):
			each_list = []
			if j == index_in_GOP_list :
				output_array.append(good_bps)
			else:
				output_array.append(bad_bps)
	
			bin_txt_name = "result-%d-4x4-1500f" % output_array[j]
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
			
		# now we begin to mix the stream
		now_flag = 0
		next_flag = 0
		active = 1
		# index_GOP is used to compte the number of VPS,SPS,PPS
		index_GOP = 0
		while (active == 1)&(index_GOP<GOP_list[index_in_GOP_list]):
			# This "if" is concern about some last line 
			if (begin_index > len(total_list[0])-len(all_binname)-2):

				for m in range(len(all_binname)):
					begin_index = begin_index + 1
					Pos, Len = getPosLen(total_list[m][begin_index])
					all_stream[m].seek(Pos,0)
					fout.write(all_stream[m].read(Len))
				active = 0
				fullfill_end_flag = True
				
			else:			
				for j in range(len(all_binname)):
					# get the string
					break_flag = 0
					
					if (now_flag + next_flag == 1):
						if (now_flag == 1)&(next_flag ==0):
							index_GOP+=1
						now_flag = 0
						next_flag = 0
						break    # this "break" breaks the "for j in range(len(all_name))" and turn back to "while"
					else:
						begin_index = begin_index + 1
						Pos, Len = getPosLen(total_list[j][begin_index])

						# when we see the .txt for different bps, in the same line(each line represent a frame ), the type of this frame must be the same
						# for example , in the 2000.txt the third line is : NALU1@ 36 : sz: 74 type:33 (SPS)
						#               in the 2250.txt the third line is : NALU1@ 36 : sz: 74 type:33 (SPS)
						# if the 2250.txt is not in the type of 33, it means that it exist the erreur
						# the "if" below shows the condition when the frame is not a normal frame, like(VPS,SPS,PPS)
						if "CODED_SLICE" not in total_list[0][begin_index]:
							#print (Len)
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
								all_stream[j].seek(Pos,0)
								
								#fout.write(bin(all_stream[0].read(Len))[2:].zfill(8))
								fout.write(all_stream[j].read(Len))
								'''
								for i in range(Len):
									stream = all_stream[0].read(1)
									fout.write(stream)
								'''
								# now_flag = 0 means that now we are in the innormal frame 
								# next_flag represent if it will change from innormal frame(VPS,PPS,SPS) to normal frame
								now_flag = 0
								next_flag = ("CODED_SLICE" in total_list[j][begin_index+1])
								print ("index = %d     Len = %d" % (begin_index,Len))
							
						else:
							# the next "for" deal with the same probleme of above
							for y in range(1,len(output_array)):
								if "CODED_SLICE" not in total_list[y][begin_index]:
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
				


				
	else:
		fullfill_end_flag = True

	return fout,fullfill_end_flag,begin_index
		
	
			
	


# This function is used to combine the function of composition
def combination(col,row,good_quality,bad_quality,GOP_list,GOP_position):
	fout = open('mm.bin','wb')
	fullfill_end_flag = False
	begin_index = 0
	for k in range(len(GOP_list)):
		if fullfill_end_flag :
			break
		else:
			fout,fullfill_end_flag,begin_index= composition(fout,k,GOP_list,GOP_position,col,row,good_quality,bad_quality,begin_index)
		
	if sum(GOP_list) < len(GOP_position):
		print ("=========================================")
		rest_begin_index = begin_index
		GOP_list.append(1000000)
		good_quality.append(good_quality[-1])
		bad_quality.append(bad_quality[-1])
		fout,fullfill_end_flag,begin_index= composition(fout,len(GOP_list)-1,GOP_list,GOP_position,col,row,good_quality,bad_quality,rest_begin_index)
	fout.close()

	
			
				
			
		
	
		
if __name__ == '__main__':
	col,row,total_frame,GOP_list,good_quality,bad_quality = readData("parameter")
	GOP_position = FindGOP("result-1000-4x4-1500f.txt")
	print(GOP_position)
	combination(col,row,good_quality,bad_quality,GOP_list,GOP_position)
	
	
