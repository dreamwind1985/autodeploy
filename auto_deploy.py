#!/usr/bin/python
import os
import paramiko
import sys

USERNAME="root"
PASSWORD="0xqinglian@ecs"
REMOTEPATH="/root/liliang/autodeploy/"
class AutoDeploy():
	def __init__(self):
		global USERNAME, PASSWORD
		self.host="123.57.185.215"
		self.username="root"
		self.password="0xqinglian@ecs"

		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(hostname=self.host, username=self.username ,password=self.password)

		self.t = paramiko.Transport(self.host, 22)
		self.t.connect(username=self.username, password=self.password)
		self.sftp = paramiko.SFTPClient.from_transport(self.t)

		self.remotepath = "/root/liliang/autodeploy/"

	def do_upload(self, dirpath):

		gz_file = self._do_compress(dirpath)
		if(gz_file == ""):
			print("do_upload failed")
			return ""
		
		rpath = os.path.abspath(self.remotepath) + "/"
		self.sftp.put(gz_file, rpath+gz_file)
		return rpath+gz_file

	def do_uncompress(self, filepath):
		dirname = os.path.dirname(filepath)
		filename = os.path.basename(filepath)
		#if os.path.isdir(dirname) == False:
		#	return ""
		#if os.path.isfile(filepath) == False:
		#	return ""
		#os.chdir(dirname)
		print "dirname:%s, filename:%s"%(dirname,filename)
		#stdin,stdout,stderr=self.ssh.exec_command("cd \"%s\"; tar -zxvf \"%s\"; sleep 30 "%(dirname, filename), get_pty=True)
		dirn =os.path.splitext( os.path.splitext(filename)[0])[0]
		dirpath = os.path.abspath(dirname)+"/"+dirn
		self.ssh.exec_command("rm -fr \"%s\""%dirpath)
		stdin,stdout,stderr=self.ssh.exec_command("cd \"%s\"; tar -zmxvf \"%s\"; sleep 30 "%(dirname, filename))
		print 'exit_code: %d' % stdout.channel.recv_exit_status()
		print stdout.read()
		print stderr.read()
		print "dirpath:%s"%dirpath
		#self.ssh.exec_command("rm -f \"%s\""%filepath)
		return dirpath
		

	def _do_compress(self, dirpath):
		tar_name = dirpath+".tar"
		gz_name = tar_name+".gz"
		if os.path.isfile(tar_name):
			os.system("rm -f "+tar_name)
		if os.path.isfile(gz_name):
			os.system("rm -f "+gz_name)
		
		os.system("tar -cf \"%s\" \"%s\""%(tar_name, dirpath))
		os.system("gzip -9 \"%s\""%tar_name)
		if os.path.isfile(gz_name):

			return gz_name
		else:
			print("compress failed")
			return ""


	def do_action(self, dirpath):
		if(dirpath == "/root/liliang/autodeploy/rabbitmq-server-3.5.6-customized" ):
			#print("rabbit")
			#stdin,stdout, stderr = self.ssh.exec_command("cd %s; rabbitmqctl stop; make -j 8;TARGET_DIR=/usr/local SBIN_DIR=/usr/local/sbin MAN_DIR=/usr/local/man make install"%dirpath)
			stdin,stdout, stderr = self.ssh.exec_command("cd %s;pwd; rabbitmqctl stop;make -j 4"%dirpath)
			print 'exit_code: %d' % stdout.channel.recv_exit_status()
			print stdout.read()
			print stderr.read()

		if(dirpath =="/root/liliang/autodeploy/otaapp"):
			stdin,stdout, stderr = self.ssh.exec_command("cd %s;pwd; rebar clean; rebar compile;cd rel; rebar generate; "%dirpath)
			print 'exit_code: %d' % stdout.channel.recv_exit_status()
			print stdout.read()
			print stderr.read()
		#os.system("cd %s; rebar clean; rebar compile; rebar generate")
			print("otaapp")
if __name__ == "__main__":

	autodeploy = AutoDeploy()
	if len(sys.argv) != 2:
		print sys.argv
		print("111111111")
	else:
		dirpath = sys.argv[1]
		rpath = autodeploy.do_upload(dirpath)
		if rpath != "":
			print "uncompress"
			rdirpath = autodeploy.do_uncompress(rpath)
			autodeploy.do_action(rdirpath)
