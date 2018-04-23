#!/usr/bin/python
# -*- coding: utf-8 -*-

from xlrd import open_workbook
from redmine import RM

import logging
from time import strftime

import sys
import configparser

def getParameters():
   # se obtienen los parámetros del sistema desde el archivo del primer parámetro
   parametros = sys.argv[1]
   log.info('Archivo de parámetros: {}'.format(parametros))
   config = configparser.ConfigParser()
   config.read(parametros, encoding='utf_8')

   # Parámetros del sistema
   par['url'] = config['Parametros del sistema']['url'].strip('"')
   par['token'] = config['Parametros del sistema']['token'].strip('"')

   par['workbook'] = sys.argv[2]
   log.info('Planilla: {}'.format(par['workbook']))

def configurar_log():
   idfile = strftime('%Y%m%d-%H%M')
   log = logging.getLogger()
   log.setLevel(logging.DEBUG)

   fh = logging.FileHandler('Log-'+idfile+'.log', mode='w')
   fh.setLevel(logging.INFO)

   # create formatter and add it to the handlers
   formatter = logging.Formatter('%(asctime)-15s, %(name)-10s, %(levelname)-6s, %(message)s')
   fh.setFormatter(formatter)

   # add the handlers to the logger
   log.addHandler(fh)
   return log, fh

def readCustomFields(s1):
    for f in range(3, s1.nrows):
        if isinstance(s1.cell(f,1).value, (int, float)):
            cFields[s1.cell(f,0).value] = int(s1.cell(f,1).value)
        else:
            log.info('El campo "{}" no tiene valor válido de identificador: "{}"'.format(s1.cell(f,0).value, s1.cell(f,1).value))
            return False
    return True

def checkValidFields(row0):
    noValidosStd = [f for f in row0 if not rm.checkFieldIsValid(f)]
    print('noValidosStd: ', noValidosStd)
    if noValidosStd:
        noValidos = set(noValidosStd - dict.keys(cFields))
        print('noValidos: ', noValidos)
        if noValidos:
            log.info('Los siguientes campos no son válidos: {}'.format(noValidos))
            return False
    log.info('Todos los campos son válidos!')
    return True

def checkValidColumns(s2, r0):
    r = True
    for j, f in enumerate(r0): # recorre columnas
        if f not in dict.keys(cFields): # sólo se controlan los campos estándar, los custom no se controlan (v1)
            for i in range(1, s2.nrows): # recorre las filas de la columna seleccionada
                cell = s2.cell(i,j).value # valor de la celda
                r1, msg = rm.checkValueisValidField(f, cell)
                if not r1:
                    log.info('La celda [{}, {}] = "{}" no tiene un valor válido de "{}" - {}'.format(i, j, cell, f, msg))
                    r = False
    if r:
        log.info('Todas las columnas son válidas')
    return r

# Hoja 1: Chequea Proyecto y tracker (tipo de petición)
def checkSheet1(s1):
    log.info('Nombre de la hoja 1: {}'.format(s1.name))
    r0c1 = s1.cell(0, 1).value
    log.info('Nombre del proyecto: {}'.format(r0c1))
    r1c1 = s1.cell(1, 1).value
    log.info('Tipo de petición: {}'.format(r1c1))

    r = rm.checkValidProject(r0c1)
    if not r:
        log.info('no existe proyecto con el nombre {}'.format(r0c1))
        r = False

    # chequea que exista el tipo de petición y que pertenezca al proyecto
    r, msg = rm.checkValidTracker(r1c1)
    if not r:
        log.info('No existe tipo de petición "{}", o no pertenece al proyecto "{}" - ({})'.format(r1c1, r0c1, msg))
    res = readCustomFields(s1)
    print('cfields:', cFields)
    return r and res

# Hoja 2
def checkSheet2(s2):
    log.info('Nombre de la hoja 2: {}'.format(s2.name))
    r0 = [(s2.cell(0, c).value, c) for c in range(s2.ncols)]
    NamesR0 = [x[0] for x in r0]
    log.info('Campos de la fila 1: {}'.format(r0))

    r = checkValidFields(NamesR0)
    if r:
        r = checkValidColumns(s2, NamesR0)
    return r

def composeCustomFields(lista, campo, valor):
    '''
    Compose a dict with: custom_fields = [{'id': 1, 'value': 'foo'}, {'id': 2, 'value': 'bar'}]
    :param lista: {nombre1: id1, nombre2: id2, ...] se arma de los parámetros
    :param campo: nombre de campo
    :param valor: valor del campo
    :return: [id del campo: valor del campo
    '''
    if campo not in lista:
        return False
    return {lista[campo]: valor}

def logprint(msg):
    log.info(msg)
    print(msg)
#-----------------------------------------------------------------
# Programa principal
#-----------------------------------------------------------------

log, fh = configurar_log()

logprint('Inicio del proceso')

par = {} # diccionario de parámetros
getParameters()

wb = open_workbook(par['workbook'])

s1 = wb.sheets()[0]
s2 = wb.sheets()[1]

rm = RM(par['url'], par['token'])

cFields = {} # lista de custom-fields leídos de la hoja 1
iData = {} # Datos para crear la petición

logprint('Se procede a validar la planilla')

if checkSheet1(s1) and checkSheet2(s2):
    logprint('Planilla válida, comienza la carga')
    for f in range(1, s2.nrows):
        iCFields = []
        for c in range(0, s2.ncols):
            field = s2.cell(0, c).value
            if field in dict.keys(cFields):
                iCFields.append({'id':cFields[field], 'value': s2.cell(f, c).value})
            else:
                iData[field] = s2.cell(f, c).value
        iData['custom_fields'] = iCFields
        print(iCFields)
        logprint('Fila: {}, Datos: {}'.format(f, iData))
        #rm.createIssue(iData)
    logprint('Fin del proceso, se crearon {} peticiones'.format(f))
else:
    logprint('Se encontraron errores en la planilla')

log.handlers.clear()
fh.close()

# Chequea que los valores de las columnas sean válidos
'''
for j, f in enumerate(f1):
    v = fields.get(f)
    if v == '*':
        for i in range(1, h2.nrows):
            cell = h2.cell(i,j).value
            #print(v, f, i, j, cell)
            if cell == '':
                print('La celda "[{}, {}]" está vacía y el campo "{}" es requerido'.format(i, j, f))
    elif v[:2] == 'id':
        for i in range(1, h2.nrows):
            cell = h2.cell(i,j).value
            print(v, f, i, j, cell)
            if not checkValuesField(v[3:], cell, pid):
                print('La celda "[{}, {}]", valor: {} no tiene un valor válido de "{}"'.format(i, j, cell, v[3:]))

        # create new issue
        issue = redmine.issue.new()
        issue.project_id = 'vacation'
        issue.subject = 'Vacation'
        issue.tracker_id = 8
        issue.description = 'foo'
        issue.status_id = 3
        issue.priority_id = 7
        issue.assigned_to_id = 123
        issue.watcher_user_ids = [123]
        issue.parent_issue_id = 345
        issue.start_date = datetime.date(2014, 1, 1)
        issue.due_date = datetime.date(2014, 2, 1)
        issue.estimated_hours = 4
        issue.done_ratio = 40
        issue.custom_fields = [{'id': 1, 'value': 'foo'}, {'id': 2, 'value': 'bar'}]
        issue.uploads = [{'path': '/absolute/path/to/file'}, {'path': '/absolute/path/to/file2'}]
        issue.save()



'''
