#!/usr/bin/env python
# coding=utf8

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


** Script para mantener los repos de localización de OCA en una instalación de ODOO
** Autor: xjimenez@capatres.com
"""

import ConfigParser
import subprocess
import shutil
import os
import sys

conf_file = 'repos.ini'
Config = ConfigParser.ConfigParser()
Config.read(conf_file)
modules_path = Config.get('general','modules_path')
branch = Config.get('general','branch')
url_base = "https://github.com/OCA/"

def exec_process(cmdline, input=None, **kwargs):
	try:
		sub = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
		stdout, stderr = sub.communicate(input=input)
		return stdout, stderr
	except OSError as e:
		print (e)
		if e.errno == 2:
			raise RuntimeError('"%s" no está presente en el sistema' % cmdline[0])  

def check_pylibs(repo):
	if os.path.exists(os.getcwd()+ "/" + repo + "/" + "requirements.txt"):
		lines = open(os.getcwd()+ "/" + repo + "/" + "requirements.txt",'r').read().splitlines()
		for line in lines:
			if line.find("#") == -1:
				line = line.split('==')[0]
				line = line.split('>=')[0]
				line = line.split('<=')[0]
				pip_command = ["pip", "show", line]
				salida, error = exec_process(pip_command, input=None)
				if len(salida) == 0:
					print "Instalamos requerimento python %s" % line 
					pip_install = ["pip", "install", line, "--user"]
					s_install, e_install = exec_process(pip_install, input=None)
					print s_install
					if len(e_install) > 0:
						print e_install
						print "Ha habido un error instalando una dependencia de python, salimos"
						sys.exit()

def check_requs(repo):
	if os.path.exists(os.getcwd()+ "/" + repo + "/" + "oca_dependencies.txt"):
		lines = open(os.getcwd()+ "/" + repo + "/" + "oca_dependencies.txt",'r').read().splitlines()
		for line in lines:
			req_repo = line.split(" ")[0]
			if req_repo not in Config.options('modules') and line.find("#") == -1 and len(req_repo) > 0:
				print "Falta dependencia OCA %s, la descargamos" % req_repo
				requ_command = ["git", "clone", url_base + req_repo + ".git", "-b", branch ]
				req_s, req_e = exec_process(requ_command, input=None)
				if len(req_e) > 0:
					print req_e
				Config.set('modules',req_repo, 1)
				cfgfile = open(conf_file,'w')
				Config.write(cfgfile)
				cfgfile.close()
				check_requs(req_repo)

def clone_or_pull_oca_repos():
	for repo in Config.options('modules'):
	 if Config.getboolean('modules',repo) == True:
		if not os.path.isdir(repo):
			print "Descargamos %s" % repo
			clone_command = ["git", "clone", url_base + repo + ".git", "-b", "10.0" ]
			clone_s, clone_e = exec_process(clone_command, input=None)
			if len(clone_e) > 0:
				print clone_e
			check_requs(repo)
			check_pylibs(repo)

		else:
			print "Actualizando " + repo
			current_dir = os.getcwd()
			pull_command = ["git", "pull"]
			os.chdir(current_dir + "/" + repo)
			pull_s, pull_e = exec_process(pull_command, input=None)
			if len(pull_e) > 0:
				print pull_e
			os.chdir(current_dir)
			check_requs(repo)
			check_pylibs(repo)

def search_and_link_modules():
	try:
		shutil.rmtree(modules_path)
		os.makedirs(modules_path)
	except:
		os.makedirs(modules_path)

	list_command = ["find", "-name", "__manifest__.py"]
	list, error = exec_process(list_command, input=None)
	for line in list.splitlines():
		if len(line) > 1:
			proj = line.split('/')[1]
			module = line.split('/')[2]
			link_command = ["ln", "-s", os.getcwd() + "/" + proj + "/" + module, modules_path + "/" + module ]
			link_s, link_e = exec_process(link_command, input=None) 
			if len(link_e) > 0:
				print link_e

def main():
	clone_or_pull_oca_repos()
	search_and_link_modules()

	print "===============================================================================================================================" + "=" * len(modules_path)
	print "Arranca odoo con ./odoo-bin -d base_de_datos -u all --without-demo=all"
	print ""
	print "Recuerda que tiene que estar definida la ruta %s en addons_path y estar la primmera, por delante de los módulos oficiales de Odoo" % modules_path
	print "===============================================================================================================================" + "=" * len(modules_path)

if __name__ == '__main__':
    main()

