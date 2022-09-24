source_folder=$1
current_dirs=()
for file in $source_folder/*
do
	if [ -d "$file" ]; then
		current_dirs+=($file)
	#	$(find $source_folder -maxdepth 1 -type d -print0)
while :
do
	for file in $source_folder/*
	do
		if [ -d "$file" ]; then
			# if we have a new run directory
			if [[ ! "${current_dirs[*]}" =~ "${file}" ]]; then
				./uploadrun_illumina.sh $source_folder/$file $file
				current_dirs+=($file)
			fi
		fi
	done
done
