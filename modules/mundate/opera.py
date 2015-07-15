#
# Common operations for web aware entities. LOL
#
# Listage::
#   echo ** this echoes 
import threading
import os, sys, re, fnmatch
import requests
import sqlalchemy
import BeautifulSoup as Soup 
from pulo import is_iterable, Eye

#
# Utility function::
#    something      ** to be printed
#    context        ** additional info for printing
#
def echo(something, **context):
    print something
    return 1

#
# Walks a path (directory) and returns files
#    returns? Filtered Content
#    path    ** to the file/directory
#    constraints ** different options ::
#        filters?
#        only_files?
#
def walk_path(path, **constraints):
    """ walk_path :: path -> {constraints} -> filtered[]"""
    echo("walk_path! -> matching! -> [filtered file-info]")
    
    filtered = []

    filters = []

    if 'filters' in constraints:
        filters = constraints['filters']
        
    only_files = False
    if 'only_files' in constraints:
        only_files = constraints['only_files']
    
    def filter_check(path):
        if len(filters) < 1:
            return True
        for filt in filters:
            m = fnmatch.fnmatch(path, filt)
            if True == m:
                return True
        return False
    
    for (path, subdirs, files) in os.walk(path):
        for filename in files:
            filepath = os.path.join(path, filename)
            if filter_check(filepath):
                filtered.append(filepath) 
        
        if not only_files:
            for dirname in subdirs:
                dirpath = os.path.join(path, dirname)
                filtered.append(dirpath)

    return filtered

#
# Reads out a file and RETURNS FILE content OBJECT
#   LOL that is simply the file in [lines]
#   PASS all needed info in the constraints, please
#
def readout_file(path, **constraints):
    echo( "readout_file :: path -> {constraints} -> [File contents]")
    lines = []
    with open(path) as f:
        for line in f:
            lines.append(line)
            
    ret = ""
    if 'return_list' in constraints and constraints['return_list'] == True:
        ret = lines
    else:
        ret = "".join(lines) 
    return ret

#
#  Takes what's left of {readout_file} and {DUMPS} it on the persistency provider
#
def dump_file(contents, **context):
    echo("dump_file :: contents -> context -> filesystem!")
    
    path = "."
    
    if 'path' in context:
        path = context['path']
        
    filename = context['filename']
    filename = os.path.join(path, filename)
    mode = "wb"
    with open(filename, mode) as f:
        f.truncate()
        if is_iterable(contents):
            for item in contents:
                f.write(item)
        else:
            f.write(contents)
        f.flush()
        
    return filename

#
# Give me an URL and I Give you RESPONSE object.
#
def download_file(url, **postguide):
    echo( "download_file :: url -> response!?" )
    local_filename = url.split('/')[-1]
    
    r = requests.get(url) #, stream=True)
    return { 'response': r, 'local_filename': local_filename} 

#
# This parses contents..
#
def parse_out(contents, **context):
    echo( "parse_out :: Parsing!" )
    #print "contents ::", contents
    tag_names = ['a']
    if 'tag_names' in context:
        tag_names = context['tag_names']
        
    soup = Soup.BeautifulSoup(contents)
    
    ret = []
    for tag_name in tag_names:
        tags = soup.findAll(tag_name)
        for tag in tags:
            ret.append(tag)
    
    return ret

#
# Upon PARSE-age EVENT, this gathers the links...
#
def gather_links(tags, **context):
    echo( "gather_links :: tags -> context -> links" )
    pass

# based on::
#  http://stackoverflow.com/questions/273192/in-python-check-if-a-directory-exists-and-create-it-if-necessary
#   
# This makes a directory, 
# path ** that is to be created
# options["parents"]?   (True/False)  ** mkdir -p?
# options["mode"]?      (Octal mode)  ** Do you need a mode &todo
# returns? { 'failed': reasons
#
def mk_dir(path, **options):
    ret = {}
    mode = 0777
    if 'mode' in options:
        mode = options['mode']

    parents = False
    
    def makedirs(f, mode):
        os.makedirs(f, mode)
        
    def mkdir(f, mode):
        pass    
        
    def ensure_dir(f, mode):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d, mode)


#
# Main Borg for doing actions on the filesystem.
#  This borg needs a lock() that is to be locked() every time a Filesystem Action
#   is to be performed
#

