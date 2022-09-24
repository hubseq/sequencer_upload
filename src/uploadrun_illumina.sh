#!/bin/bash

# run counter
i=0
run_done=0
dest_bucket="mock-sequencer-illumina"
source_folder=$1
final_file="RTAComplete.txt"
num_files_previous=0

# loop and run rclone copy until sequencing run is done
while [ $run_done -le 3 ]
do
	rclone copy --max-age 24h --no-traverse $source_folder/ s3:$dest_bucket/$2/ -P

	# traverse the files and count # of files. Also look for Complete file. Can traverse 9 layers deep (Illumina goes at least 8 deep)
	let final_file_found=0
	let num_files=0

	# NOTE: find has issues with files with spaces. ls has other issues.
	for file in $source_folder/*
	do
		if [ -d "$file" ]; then
			for file2 in $file/*
			do
				if [ -d "$file2" ]; then
					for file3 in $file2/*
					do
						if [ -d "$file3" ]; then
							for file4 in $file3/*
							do
								if [ -d "$file4" ]; then
									for file5 in $file4/*
									do
										if [ -d "$file5" ]; then
											for file6 in $file5/*
											do
												if [ -d "$file6" ]; then
													for file7 in $file6/*
													do
														if [ -d "$file7" ]; then
															for file8 in $file7/*
															do
																if [ -d "$file8" ]; then
																	for file9 in $file8/*
																	do
																		if [ -d "$file9" ]; then
																			for file10 in $file9/*
																			do
																				(( num_files++ ))
																			done
																		else
																			(( num_files++ ))
																		fi
																	done
																else
																	(( num_files++ ))
																fi
															done
														else
															(( num_files++ ))
														fi
													done
												else
													(( num_files++ ))
												fi
											done
										else
											(( num_files++ ))
										fi
									done
								else
									(( num_files++ ))
								fi
							done
						else
							(( num_files++ ))
						fi
					done
				else
					(( num_files++ ))
				fi
			done
		else
			(( num_files++ ))
		fi

		# check if RTAComplete.txt file exists
		if [ $file == "$source_folder/$final_file" ]
		then
			let final_file_found=1
		fi
	done
	
	echo $num_files
	echo $final_file_found

	# if final file found and no new files have been uploaded, then we are done.
	if [ $final_file_found -eq 1 ] && [ $num_files -eq $num_files_previous ]
	then
		(( run_done++ ))
	else
		let run_done=0
	fi

	# wait before next copy
	echo $run_done
	let num_files_previous=$num_files
	sleep 15
done
# upload the final checksum file
checksum_md5=$(find $source_folder -type f ! -name "CHECKSUM.MD5" -exec md5sum {} + | LC_ALL=C sort | md5sum)
echo $checksum_md5 > $source_folder/CHECKSUM.MD5
rclone copy --max-age 24h --no-traverse $source_folder/ s3:$dest_bucket/$2/ -P
echo "upload DONE!"
