### NasMyCloudToS3
#### Python script to upload files and folders to Amazon S3 from NAS my Cloud EX4100 (Western Digital).

##### Advise
This script uses the binary called *s3* which is included in the NAS EX4100 firmware. Don't use if you don't have this binary file.

##### Instructions
1. Copy the files **nastos3.py** and **file.conf** to a directory in your NAS.
2. Config file **file.conf** with your parameters. Here is a description:
       
	- **_bucket_**: The name of the bucket where you want upload the folder.
	- **_access_key_**: Your access key for the bucket.
	- **_secret_key_**: Your secret key for the bucket.
	- **_remote_path_**: To upload files inside a folder. If empty the upload process begin in the root of the bucket. Do not add slash at the beggining. Example: **example/**
	- **_origin_path_**: Origin path of the folder that you want upload. Do not add the final slash. Example: **my/folder/that/i/want/upload** 
              
3. Start the script with this command:
        
		python nastos3.py -i file.conf -l /path/to/log/mylog.log
 
	where:
    	**_-i_** Name of the .conf file. 
    	**_-l_** Path to the log file. Can be only the name of the log, in which case the log file are stored in the actual folder.
            
4. And that is all.
