#!/usr/bin/python
# coding=utf-8
__revision__ = "2015.03.03"
__appname__  = "innmall"
__author__   = "shuxiang29"
__email__    = "shuxiang29@gmail.com"

import os
import platform
from git.cmd import Git
from git.repo.base import DefaultDBType
from git.repo.base import Repo

class MacRepo(Repo):

    def __init__(self, path=None, odbt=DefaultDBType):
        """Create a new Repo instance extends from git.Repo

        :param path: is the path to either the root git directory or the bare git repo::

            repo = Repo("/Users/mtrier/Development/git-python")
            repo = Repo("/Users/mtrier/Development/git-python.git")
            repo = Repo("~/Development/git-python.git")
            repo = Repo("$REPOSITORIES/Development/git-python.git")
        
        :param odbt: Object DataBase type - a type which is constructed by providing 
            the directory containing the database objects, i.e. .git/objects. It will
            be used to access all object data
        :raise InvalidGitRepositoryError:
        :raise NoSuchPathError:
        :return: git.Repo """
        super(MacRepo, self).__init__(path, odbt)

    @classmethod
    def init(cls, path=None, mkdir=True, **kwargs):
        """Initialize a git repository at the given path if specified

        :param path:
            is the full path to the repo (traditionally ends with /<name>.git)
            or None in which case the repository will be created in the current 
            working directory

        :parm mkdir:
            if specified will create the repository directory if it doesn't
            already exists. Creates the directory with a mode=0755. 
            Only effective if a path is explicitly given

        :parm kwargs:
            keyword arguments serving as additional options to the git-init command

        :return: ``git.Repo`` (the newly created repo)"""

        if mkdir and path and not os.path.exists(path):
            os.makedirs(path, 0755)

        # git command automatically chdir into the directory
        git = Git(path)
        output = git.init(**kwargs)
        return MacRepo(path)
        
    @property
    def untracked_files(self):
        """
        :return:
            list(str,...)
            
            Files currently untracked as they have not been staged yet. Paths 
            are relative to the current working directory of the git command.
            
        :note:
            ignored files will not appear here, i.e. files mentioned in .gitignore"""
        # make sure we get all files, no only untracked directores
        proc = self.git.status(untracked_files=True, as_process=True)
        stream = iter(proc.stdout)
        untracked_files = list()
        for line in stream:
            if not line.startswith("Untracked files:"):
                continue
            # skip five lines
            stream.next()
            stream.next()
            
            for untracked_info in stream:
                if not untracked_info.startswith("\t"):
                    break
                untracked_files.append(untracked_info.replace("\t", "").rstrip())
            # END for each utracked info line
        # END for each line
        return untracked_files

class Revisioncontrol(object):

    def __init__(self, path):
        if path=="":
            raise 'repo path can not be empty'
        else:
            self.path = path
            if 'Darwin' in platform.system():
                self.repo=MacRepo.init(self.path)
            else:
                self.repo=Repo.init(self.path)

    def listUntrackedFiles(self):
        """
            对于版本库来说,untracked files就是本地新增的文件，返回新增文件的绝对路径
        """
        untrackedFiles=[]
        for untrackedFile in self.repo.untracked_files:
            untrackedFiles.append(self.repo.working_dir+'/'+untrackedFile)
        return untrackedFiles

    def isModified(self):
        """
            判断版本库是否修改过（即有无new file、modified等，不包含untracked files）
        """
        return self.repo.is_dirty()

    def listModifiedFiles(self):
        """
            获取修改文件路径的列表，是文件的绝对路径
        """
        modifiedFiles=[]
        headCommit=self.repo.head.commit
        diffs=headCommit.diff(None, paths=self.path)
        for diff in diffs.iter_change_type('M'):
            modifiedFiles.append(diff.b_blob.abspath)
        return modifiedFiles

    def listNewFiles(self):
        """
            获取新增文件路径的列表，是文件的绝对路径
        """
        newFiles=[]
        headCommit=self.repo.head.commit
        diffs=headCommit.diff(None, paths=self.path)
        for diff in diffs.iter_change_type('A'):
            newFiles.append(diff.b_blob.abspath)
        return newFiles

    def getDiff(self,filePath=None):
        """
            获取传入的文件差异信息
            @param filePath: 差异获取路径
        """
        filePath = filePath or self.repo.working_dir
        return self.repo.git._call_process('diff', filePath)

    def commitToRepo(self,comment):
        """
            将所有暂存区的修改或者新增提交到版本库
            @param comment: 版本库提交注释
        """
        if comment==None or comment=='':
            raise '提交到版本库时注释不能为空'
        self.repo.git._call_process('commit', m=comment)

    def addToStage(self, path=None):
        """
            将所有新增或者修改添加到暂存区
        """
        if path is None:
            self.repo.git._call_process('add', '*')
        else:
            self.repo.git._call_process('add', path.rstrip('/')+'/*')

if __name__ == '__main__':
    revisioncontrol = Revisioncontrol('/Users/haokuan/bitbucket/file/fhspider/Revisioncontrol/webcrawl/ctrip')
    revisioncontrol.addToStage()