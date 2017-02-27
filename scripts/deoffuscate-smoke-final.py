#!/usr/bin/env python2
# coding=utf8

#
# Desofusca el completamente el js ofiscado para smoke
# Morbith <xjr00t@gmail.com>

import re

def procesa_valores(valores):
 if re.search('\[.*?\]\[\d+\]',valores):
	for match in re.findall('\[.*?\]\[\d+\]',valores):
		flag = False
		if match[:2] == '[[':
			flag = True
		indice = re.search('\[\d*?\]',match).group()
		indice = re.search('\d+',indice).group()
		datos = re.findall('\[.*?\]',match)[0][1:]
		dato = datos.split(',')[int(indice)].strip('[]').strip()
		if flag:
			valores = '['+valores.replace(match,dato)
		else:
			valores = valores.replace(match,dato)
			
 if re.search('.*?\[\d+\]\[.*?\[\d+\]\]\(.*?\[\d+\]\)',valores):
	resultados = []
	for part in re.findall('\w*?\[\d*?\]',valores):
		indice = re.search('\[\d+\]',part).group()
		indice = re.search('\d+',indice).group()
		datos_array = globals().get(re.findall('\w*',part)[0])
		dato = datos_array.split(', ')[int(indice)]
		if dato[:1] == '[':
			dato = dato[1:]
		if dato[-1:] == ']':
			dato = dato[:-1]
		resultados.append( dato )
	valores = resultados[0]+"["+resultados[1]+"]("+resultados[2]+")"
 return valores 

def valor_variable(variable, indice):
	if indice == True:
		indice = re.search('\[\d*?\]',variable).group()
		indice = re.search('\d+',indice).group()
		datos_array = globals().get(re.findall('\w*',variable)[0])
		dato = datos_array.split(', ')[int(indice)]
		if dato[:1] == '[':
			dato = dato[1:]
		if dato[-1:] == ']':
			dato = dato[:-1]
		return dato
	else:
		dato = globals().get(re.findall('\w*',variable)[0])
		return dato

def sustituye_variables(linea):
	for variable in variables:
	 if linea.find(variable) > 0:
		 if re.search(variable+'\[\d+\]',linea):
			dato = valor_variable( re.search(variable+'\[\d+\]',linea).group(), True )
			linea = linea.replace(re.search(variable+'\[\d+\]',linea).group(),dato)
		 else:
			 dato = valor_variable( re.search(variable,linea).group(), False )
			 linea = linea.replace(re.search(variable,linea).group(),dato)
			 
	return linea		

def resuelve_array(array):
	for match in re.findall('\[.*?\]\[\d+\]',array):
		indice = re.search('\[\d*?\]',array).group()
		indice = re.search('\d+',indice).group()
		#datos = re.search('new\[.*?\]',array).group()
		dato = re.search('\[.*?\].+',array).group()
		dato = dato.split(', ')[int(indice)]
		
		if dato[:1] == '[':
			dato = dato[1:]
		if dato[-1:] == ']':
			dato = dato[:-1]		
		return dato
		

def deoffuscate_payload(jscript):
	variables = []
	for i in re.findall('\$\w*?=.*?\';',jscript):
		vn = i.split("=")[0][1:]
		cont = re.findall('=.*?\';',i)[0][1:-1]
		variables.append(vn)
		globals()['%s' % vn] = cont

	for variable in variables:
		jscript = jscript.replace('$'+variable+'='+globals().get(variable)+";", "")		
		jscript = jscript.replace('$'+variable+'+',globals().get(variable)[2:-1])
		jscript = jscript.replace('$'+variable+')',globals().get(variable)[2:-1])
		
	array_new = re.findall('new\[.*?\]\[\d+\]',jscript)[0]
	raw_new   = re.findall('\[.*?\]\[\d+\]',array_new)
	dato = resuelve_array ( raw_new[0] )
	jscript = jscript.replace( array_new, dato )
	array_final = re.findall('\[.*?\]\[\d+\]',jscript)[0]
	dato = resuelve_array ( array_final )
	jscript = jscript.replace( array_final, dato )		
	return jscript
	
	
fp = open('smokedownloader.js','r')
fc = fp.read()
data = fc.split(';\n')

variables = []

text = ''

for line in data:
	if re.search('^var .+', line):
	 variables.append(line.split(" ")[1])
	 globals()['%s' % line.split(" ")[1]] = str(procesa_valores(line.split(" = ")[1].strip()))
	else:
	 text += sustituye_variables(line)

text = text.split('" + "')
text = "".join(text)

print deoffuscate_payload(text)
