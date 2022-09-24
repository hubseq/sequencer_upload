have one script that just looks for new run directories. This script runs all the time.
If a new run directory is created, then run a 2nd script that uploads that run to the cloud. That 2nd script will finish when the RTAComplete.txt file is found and there are no more files in the directory.
A final checksum should be calculcated, and saved as CHECKSUM.MD5, and uploaded along with sequencing data. On the backend, I should have a lambda function that downloads all the data and verifies the checksum.
I should also have a function that checks sequencing runs finished in previous days. If the checksum is different than the supposed complete CHECKSUM.MD5, then we should re-upload that run. Make sure not to include the checksum file in that check.
