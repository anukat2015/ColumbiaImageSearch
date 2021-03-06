import os
import requests
import shutil
import time
import warnings
import numpy as np

imagedltimeout = 3
session = requests.Session()
session.trust_env = False
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def mkpath(outpath):
    pos_slash=[pos for pos,c in enumerate(outpath) if c=="/"]
    for pos in pos_slash:
        try:
            os.mkdir(outpath[:pos])
        except:
            pass

def dlimage_basepath(url,basepath,logf=None):
    start_time = time.time()
    if not url:
        return None
    pos_slash=[pos for pos,c in enumerate(url) if c=="/"]
    #pos_point=[pos for pos,c in enumerate(url) if c=="."]
    if not pos_slash:
        return None
    file_img=url[pos_slash[-1]+1:]
    # path with time and random to ensure unique names
    outpath=os.path.join(basepath,str(time.time())+'_'+str(np.int32(np.random.random()*(10e6)))+'_'+file_img)
    mkpath(outpath)
    uptomkpath_time = time.time()
    #print "Downloading image from {} to {}.".format(url,outpath)
    try:
        #r = requests.get(url, stream=True, timeout=imagedltimeout)
        # still slow with session.trust_env
        # verify=False induces a InsecureRequestWarning
        r = session.get(url, stream=True, timeout=imagedltimeout, verify=False)
        uptorequest_time = time.time()
        if r.status_code == 200:
            with open(outpath, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            uptowrite_time = time.time()
            mkpath_time = uptomkpath_time - start_time
            dl_time = uptorequest_time - uptomkpath_time
            write_time = uptowrite_time - uptorequest_time
            print("[dlimage_basepath] mkpath_time {}, dl_time {}, write_time {}".format(mkpath_time, dl_time, write_time))
            return outpath
    except Exception as inst:
        if logf:
            logf.write("Download failed for img that should be saved at {} from url {}.\n".format(outpath,url))
        else:
            print "Download failed for img that should be saved at {} from url {}.".format(outpath,url)
        print inst 
    return None


def dlimage_basepath_integritycheck(url, basepath, logf=None):
    import subprocess as sub
    if not url:
        return None
    pos_slash = [pos for pos,c in enumerate(url) if c=="/"]
    if not pos_slash:
        return None
    file_img = url[pos_slash[-1]+1:]
    # path with time and random to ensure unique names
    outpath = os.path.join(basepath,str(time.time())+'_'+str(np.int32(np.random.random()*(10e6)))+'_'+file_img)
    mkpath(outpath)
    #print "Downloading image from {} to {}.".format(url,outpath)
    try:
        #r = requests.get(url, stream=True, timeout=imagedltimeout)
        # verify=False induces a InsecureRequestWarning
        r = session.get(url, stream=True, timeout=imagedltimeout, verify=False)
        if r.status_code == 200:
            if int(r.headers['content-length']) == 0:
                raise ValueError("Empty image.")
            with open(outpath, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            # integrity check here
            ok_tag = '[OK]'
            error_tag = '[ERROR]'
            command = 'jpeginfo -c '+ outpath
            output, error = sub.Popen(command.split(' '), stdout=sub.PIPE, stderr=sub.PIPE).communicate()
            if output.find(ok_tag)<0 or output.find(error_tag)>=0:
                # some images are not JPEG, either PNG or even HTML...
                raise ValueError("Integrity check failed, output was: {}".format(output.strip()))
            return outpath
    except Exception as inst:
        if logf:
            logf.write("[dlimage_basepath_integritycheck: error] Download failed for img that should be saved at {} from url {}. {}\n".format(outpath, url, inst))
        else:
            print "[dlimage_basepath_integritycheck: error] Download failed for img that should be saved at {} from url {}. {}".format(outpath, url, inst)
    return None


def dlimage(url,logf=None):
    return dlimage_basepath(url,'./',logf)


def dlimage_args(args):
    if len(args)==2:
       #print args[0],args[1]
       return dlimage_basepath(args[0],args[1])    
    else:
       print "[dl_image_args: warning] incorrect agruments: {}.".format(args)
       return None


def dlimage_args_integritycheck(args):
    if len(args)==2:
       #print args[0],args[1]
       return dlimage_basepath_integritycheck(args[0], args[1])    
    else:
       print "[dl_image_args_integritycheck: warning] incorrect agruments: {}.".format(args)
       return None
