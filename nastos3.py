#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import getopt
import ConfigParser
import traceback
import logging
import subprocess
import hashlib

BUCKET = ''
ACCESS_KEY = ''
SECRET_KEY = ''
ORIGIN_PATH = ''
INPUTFILE = ''
REMOTE_PATH = ''

def main(argv):
    try:
        opts, arg = getopt.getopt(argv, "i:l:", ["inputfile","logfile"])
    except getopt.GetoptError:
        logging.error('Input file error')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-i':
            inputFile = arg
        if opt == '-l':
            LOGFILE = arg
    if LOGFILE:
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p',
                            filename=LOGFILE, level=logging.INFO)
    logging.info('--------------------Init upload session--------------------')
    if checkFile(inputFile):
        logging.info('Configuration file is good')
        setEnvironment()
        uploadAFile()
    else:
        logging.error('File is not good. Check the file')
        sys.exit(0)

def getMD5Base64(filename):
    hash = hashlib.md5()
    with open(filename) as f:
        for chunk in iter(lambda: f.read(4096), ""):
            hash.update(chunk)
    return hash.digest().encode('base64').strip()

def setEnvironment():
    global ACCESS_KEY
    global SECRET_KEY
    logging.info('Setting environment variables')
    os.environ["S3_ACCESS_KEY_ID"] = ACCESS_KEY
    logging.info('Variable S3_ACCESS_KEY_ID=*******' + str(os.environ.get('S3_ACCESS_KEY_ID'))[-5:])
    os.environ["S3_SECRET_ACCESS_KEY"] = SECRET_KEY
    logging.info('Variable S3_SECRET_ACCESS_KEY=*******' + str(os.environ.get('S3_SECRET_ACCESS_KEY'))[-5:])
    logging.info('Setted environment variables')

def checkFile(inputfile):
    global BUCKET
    global ACCESS_KEY
    global SECRET_KEY
    global ORIGIN_PATH
    global REMOTE_PATH
    checkFileBool = True
    config = ConfigParser.ConfigParser()
    config.read(inputfile)
    BUCKET = config.get('Job_1', 'bucket')
    logging.info('Bucket: ' + BUCKET)
    ACCESS_KEY = config.get('Job_1', 'access_key')
    SECRET_KEY = config.get('Job_1', 'secret_key')
    ORIGIN_PATH = config.get('Job_1', 'origin_path')
    logging.info('Origin path: ' + ORIGIN_PATH)
    REMOTE_PATH = config.get('Job_1', 'remote_path')
    if REMOTE_PATH:
        logging.info('Remote path: ' + REMOTE_PATH)
    if not BUCKET or not ACCESS_KEY or  not SECRET_KEY or not ORIGIN_PATH:
        checkFileBool = False
    return checkFileBool

def uploadAFile():
    try:
        global BUCKET
        global ACCESS_KEY
        global SECRET_KEY
        global ORIGIN_PATH
        global REMOTE_PATH
        ORIGIN_PATH = ORIGIN_PATH.decode().encode('utf-8')
        logging.info('Initializing upload of files')
        for dirName, subdirList, fileList in os.walk(ORIGIN_PATH):
            for filename in fileList:
                file = os.path.join(dirName, filename)
                filemd5 = str(getMD5Base64(file))
                fileSize = os.path.getsize(file)
                fileObject = file.replace(ORIGIN_PATH,'')
                fileObject = fileObject.replace('///', '/')
                if REMOTE_PATH:
                    fileObject = BUCKET + '/' + REMOTE_PATH + fileObject
                s3md5 = subprocess.Popen(['/usr/local/modules/usrsbin/s3 head "' + fileObject + '" | grep x-amz-meta-md5'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = s3md5.communicate()
                subir = True
                if out:
                    out = str(out)
                    out = out.replace('x-amz-meta-md5: ','').replace(' ','').replace('\n','')
                    if filemd5 == out:
                        subir = False
                    else:
                        subir = True
                if err:
                    err = str(err)
                    err = err.replace('\n','')
                    if err.find('HttpErrorNotFound') != -1:
                        subir = True
                    else:
                        subir = False
                if subir:
                    with open(file, 'rb') as data:
                        logging.info('Uploading: ' + file)
                        q = subprocess.check_output(['/usr/local/modules/usrsbin/s3 put "' + fileObject +
                                                '" filename="' + file + '" contentLength=' + str(fileSize) + ' md5=' + filemd5 + ' x-amz-meta-md5=' + str(filemd5) + ' | grep status'], stderr=subprocess.STDOUT, shell=True)
                        #output, err = q.communicate()
                        q = str(q)
                        q = q.replace("ERROR: Nondigit in TotalSize parameter:",'').replace('\n','')
                        logging.info("Upload finished." + q + ". (Status = 0 means it's all OK)")
                else:
                        logging.info('The file ' + file + ' is the same in s3. Skipping')
        logging.info('All files uploaded to bucket ' + BUCKET)
    except Exception as err:
        traceback.print_exception
        logging.error(err)

if __name__ == "__main__":
    main(sys.argv[1:])
