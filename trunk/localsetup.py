import os, sys
from os.path import isfile, isdir, join


#enter your defaults here
#HOME is not used in the script, but this script is
#design for installation in a home directory
#except in defining defaults
HOME = os.environ['HOME']
#binpath should be in $PATH
binpath = join(HOME, 'bin')
#pythonpath can be /usr/local/lib/python2.3/site-packages
#or something similar, but the modules are not installed, just
#symlinked.
#in .bashrc export PYTHONPATH=pythonpath
pythonpath = join(HOME, 'local/python')
#workspace is where the working copies will checked out to
workspace = join(HOME, 'workspace')
#this default is probably ok
svnrepos = 'svn://svn.berlios.de/svnroot/repos'
#set runme to True for this script to work
runme = False


def checkout(project, path):
    npath = join(path, project)
    if not isdir(npath):
        svnroot = svnrepos + '/%s/trunk' % project
        cmd = 'svn co %s %s' % (svnroot, npath)
        print cmd
        os.system(cmd)
        

def setup_pythonpath():
    if not isdir(pythonpath):
        os.system('mkdir -p %s' % pythonpath)
    if not os.environ.has_key('PYTHONPATH'):
         os.environ['PYTHONPATH'] = pythonpath

def setup_binpath():
    if not isdir(binpath):
        os.system('mkdir -p %s' % binpath)
        
def setup_paella(path):
    ppath = join(path, 'paella/src/paella')
    os.system('ln -s %s %s' % (ppath, pythonpath))

def setup_konsultant(path):
    ppath = join(path, 'konsultant/lib/konsultant')
    bpath = join(path, 'konsultant/konsultant')
    os.system('ln -s %s %s' % (ppath, pythonpath))
    os.system('ln -s %s %s' % (bpath, binpath))
    
if __name__ == '__main__':
    if not runme:
        print 'please review defaults first'
        sys.exit(1)

    setup_pythonpath()
    setup_binpath()

    projects = ['paella', 'konsultant']
    for project in projects:
        checkout(project, workspace)
    
    setup_paella(workspace)
    setup_konsultant(workspace)
    
