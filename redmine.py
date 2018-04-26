#!/usr/bin/python

from redminelib import Redmine
import datetime
import os

class RM():
    def __init__(self, url, token):
        '''
        Se conecta a la instancia redmine a través de la API redminelib y crea el objeto 'project'
        que usa en el resto de las funciones
        :param url: la dirección del ambiente redmine a conectarse
        :param token: El token del usuario con que se conecta
        :param projectName: Nombre del proyecto (tal como aparece para el usuario final)
        '''
        self.redmine = Redmine(url, key=token)
        self.project = self. tracker = None

        # 'fieldname': {'required': 'yes|no', 'type': 'id|date|text|int|%|file|issue', 'id': 'keyname'}
        self.fields = {
            'Asunto': {'required': 'yes', 'type': 'text'},
            'Descripción': {'required': 'yes', 'type': 'text'},
            'Estado': {'required': 'yes', 'type': 'id', 'id': 'status'},
            'Prioridad': {'required': 'no', 'type': 'id', 'id': 'priority'},
            'Asignado a': {'required': 'no', 'type': 'id', 'id': 'user'},
            'Categoría': {'required': 'yes', 'type': 'id', 'id': 'category'},
            'Fecha de inicio': {'required': 'no', 'type': 'date'},
            'Fecha fin': {'required': 'no', 'type': 'date'},
            'Ficheros': {'required': 'no', 'type': 'file'},
            'Tarea padre': {'required': 'no', 'type': 'issue'},
            'Tiempo estimado': {'required': 'no', 'type': 'int'},
            '% Realizado': {'required': 'no', 'type': '%'}
             }
        self.trackers = self.statuses = self.priorities = self.categories = self.roles = None

    def checkValidProject(self, projectName):
        '''
        :return: Devuelve el objeto 'project'
        '''
        try:
            projects = self.redmine.project.all()
            self.project = [x for x in projects if x.name == projectName][0]
            return self.project
        except:
            raise ValueError('Hubo error en la conexión o bien no existe proyecto con ese nombre')
            return False

    def checkValidTracker(self, trackerName):
        msg = 'Ok'
        r = True
        if not self.trackers:
            self.trackers = self.redmine.tracker.all()
        try:
            self.tracker = [x for x in self.trackers if x.name == trackerName][0]
            if not self.chkTrackerInProject(self.tracker.id):
                msg = 'No tracker in project'
                r = False
        except:
            msg = 'tracker does not exist'
            r = False
        return r, msg

    def checkValidIssueId(self, id):
        if isinstance(id, (int, float)):
            try:
                issue = self.redmine.issue.get(int(id))
                return True
            except:
                return False


    def idStatus(self, statusName):
        '''
            :param statusName: Nombre del estado ('Nueva', 'Pendiente', etc.)
            :return: Devuelve el id del estado o False si no existe
        '''
        if not self.statuses:
            self.statuses = self.redmine.issue_status.all()
        try:
            s = [x for x in self.statuses if x.name == statusName][0]
            return s.id
        except:
            return False

    def idCategory(self, categoryName):
        '''
            :param categoryName: Nombre de la categoría
            :return: Devuelve el id de la categoría o False si no existe
        '''
        if not self.categories:
            self.categories = self.redmine.issue_category.filter(project_id=self.project.id)
        try:
            c = [x for x in self.categories if x.name == categoryName][0]
            return c.id
        except:
            return False

    def idPriority(self, priorityName):
        '''
            :param priorityName: Nombre de la prioridad
            :return: Devuelve el id de la prioridad o False si no existe
        '''
        if not self.priorities:
            self.priorities = self.redmine.enumeration.filter(resource='issue_priorities')
        try:
            p = [x for x in self.priorities if x.name == priorityName][0]
            return p.id
        except:
            return False

    def idUser(self, userName):
        '''
            :param userName: Nombre del usuario
            :return: Devuelve el id del usuario o False si no existe
        '''
        try:
            users = self.redmine.user.filter(name=userName)
            return users[0].id
        except:
            return True

    def idRol(self, rolName):
        '''
            :param rolName: Nombre del rol
            :return: Devuelve el id del rol o False si no existe
        '''
        if not self.roles:
            self.roles = self.redmine.role.all()
        try:
            r = [x for x in self.roles if x.name == rolName][0]
            return r.id
        except:
            return False

    def checkFieldIsValid(self, fieldName):
        return fieldName in dict.keys(self.fields)

    def checkValueisValidField(self, field, value):
        r = True
        msg = 'Ok'
        if not field in self.fields:
            r = False
            msg = 'field does not exist'.format(field)
            return r, msg
        f = self.fields[field]
        if value == '' and f['required'] == 'yes':
            r = False
            msg = 'required field'
        if value != '':
            if f['type'] == 'id':
                if f['id'] == 'status':
                    r = self.idStatus(value)
                elif f['id'] == 'category':
                    r = self.idCategory(value)
                elif f['id'] == 'user':
                    idU = self.idUser(value)
                    if idU:
                        r = self.checkUserIdInProject(idU)
                    else:
                        r = False
                elif f['id'] == 'priority':
                    r = self.idPriority(value)
                if not r:
                    msg = 'Value not valid'
            elif f['type'] == 'date' and not isinstance(value, (float, int, datetime.datetime)):
                r = False
                msg = 'Not valid date format (int, float or datetime)'
            elif f['type'] == 'file' and not os.path.exists(value):
                r = False
                msg = 'file does not exist'
            elif f['type'] == 'int' and not isinstance(value, int):
                r = False
                msg = 'Not valid int format'
            elif f['type'] == '%' and not (isinstance(value, int) or value in range(0, 100)):
                r = False
                msg = 'Not valid % value'
            elif f['type'] == 'issue' and not self.checkValidIssueId(value):
                r = False
                msg = 'Not valid issue ID'
        return r, msg

    def checkUserNameInProject(self, userName):
        '''
            :param userName: Nombre del usuario
            :return: Devuelve True o False según si el usuario pertenece o no al proyecto
        '''
        m = self.project.memberships
        return any(user == x.user['name'] for x in m if hasattr(x, 'user'))
        #return set([(x.user['id'], x.user['name']) for x in m for y in x.roles if y.id == rol and hasattr(x, 'user')])

    def checkUserIdInProject(self, userId):
        '''
            :param userId:
            :return: Devuelve True o False según si el id usuario pertenece o no al proyecto
        '''
        m = self.project.memberships
        return any(userId == x.user['id'] for x in m if hasattr(x, 'user'))

    def chkUserInProjectRol(self, userId, rolId):
        '''
            :param userId: id del usuario
            :param rolId: id del rol
            :return: Verifica que un Id de usuario pertenezca a un proyecto en un determinado rolId
        '''
        u = self.listUsersInProjectRol(rolId)
        return userId in [x[0] for x in u]

    def chkTrackerInProject(self, idTracker):
        '''
            :param idTracker: tracker Id
            :return: Verifica, por id, que el tipo de petición pertenezca a un proyecto
        '''
        return idTracker in [x.id for x in self.project.trackers]

    def convertToDate(self, value):
        return value if isinstance(value, datetime.datetime) \
            else datetime.datetime.utcfromtimestamp((value - 25569) * 86400.0 ).date()

    def createIssue(self, fieldsDict):
        issue = self.redmine.issue.new()
        issue.project_id = self.project.id
        issue.tracker_id = self.tracker.id
        if 'Asunto' in fieldsDict and fieldsDict['Asunto'] != '':
            issue.subject = fieldsDict['Asunto']
        if 'Descripción' in fieldsDict and fieldsDict['Descripción'] != '':
            issue.description = fieldsDict['Descripción']
        if 'Estado' in fieldsDict and fieldsDict['Estado'] != '':
            issue.status_id = self.idStatus(fieldsDict['Estado'])
        if 'Prioridad' in fieldsDict and fieldsDict['Prioridad'] != '':
            issue.priority_id = self.idPriority(fieldsDict['Prioridad'])
        if 'Categoría' in fieldsDict and fieldsDict['Categoría'] != '':
            issue.category_id = self.idCategory(fieldsDict['Categoría'])
        if 'Asignado a' in fieldsDict and fieldsDict['Asignado a'] != '':
            issue.assigned_to_id = self.idUser(fieldsDict['Asignado a'])
        if 'Fecha de inicio' in fieldsDict and fieldsDict['Fecha de inicio'] != '':
            issue.start_date = self.convertToDate(fieldsDict['Fecha de inicio'])
        if 'Fecha fin' in fieldsDict and fieldsDict['Fecha fin'] != '':
            issue.due_date = self.convertToDate(fieldsDict['Fecha fin'])
        if 'custom_fields' in fieldsDict and fieldsDict['custom_fields'] != '':
            issue.custom_fields = fieldsDict['custom_fields']
        if 'Ficheros' in fieldsDict and fieldsDict['Ficheros'] != '':
            issue.uploads =  [{'path': fieldsDict['Ficheros']}]
        if 'Tarea padre' in fieldsDict and fieldsDict['Tarea padre'] != '':
            issue.parent_issue_id = fieldsDict['Tarea padre']
        if 'Tiempo estimado' in fieldsDict and fieldsDict['Tiempo estimado'] != '':
            issue.estimated_hours = fieldsDict['Tiempo estimado']
        if '% Realizado' in fieldsDict and fieldsDict['% Realizado'] != '':
            issue.done_ratio = fieldsDict['% Realizado']

        # Atención, el siguiente campo no está probado!

        if 'watcher_user_ids' in fieldsDict and fieldsDict['watcher_user_ids'] != '':
            issue.watcher_user_ids = fieldsDict['watcher_user_ids']

        issue.save()
        return


    def listTrackersInProject(self):
        '''
            :return: Devuelve la lista de id y nombre de los tipos de petición del proyecto
        '''
        return [(x.id, x.name) for x in self.project.trackers]

    def listUsersInProjectRol(self, rolId):
        '''
            :param rolId: Id del rol
            :return: Lista id y nombre de todos los usuarios de un proyecto que tienen un rol determinado
        '''
        m = self.project.memberships
        return set([(x.user['id'], x.user['name']) for x in m for y in x.roles if y.id == rolId and hasattr(x, 'user')])

    def listGroupsInProjectRol(self, rolId):
        '''
            :param rolId:
            :return: Lista id y nombre de todos los grupos de usuarios de un proyecto que tienen un rol determinado
        '''
        m = self.project.memberships
        return set([(x.group['id'], x.group['name']) for x in m for y in x.roles if y.id == rolId and hasattr(x, 'group')])

    def listCategoriesInProject(self):
        '''
            :return: Devuelve la lista de id y nombre de las categorías del proyecto
        '''
        return [(x.id, x.name) for x in self.project.issue_categories]

if __name__ == "__main__":
    '''
    def attach(path, filename, description, content_type):
        # [{'path': '/absolute/path/to/file'}, {'path': '/absolute/path/to/file2'}]
    '''
    proj = 'Soporte' #'z_Aprobación de Requerimientos'
    track = 'Soporte' #'Aprobación de documentos'
    user = 'Luis Cibils'
    status = 'Aprobado'
    category = 'Cableado' #'Requerimiento'
    priority = 'Normal'
    rol = 'Soporte'
    userExiste = 'Nicolas Correa'
    userNoExiste = 'Juan'

    url = 'https://colo1.msp.gub.uy/redmine/'
    token = '7912b4cc1a85bbc3f0f8637bac2329d80a1a66a9'
    p = RM(url, token)

    print('id project: ', p.checkValidProject(proj))
    print('id tracker: ', p.idTracker(track))
    print('id status:', p.idStatus(status))
    print('id category:', p.idCategory(category))
    print('id user:', p.idUser(user))
    print('id priority:', p.idPriority(priority))
    print('id rol:', p.idRol(rol))
    print('categorias de un proyecto: ', p.listCategoriesInProject())
    print('tipos de petición de un proyecto: ', p.listTrackersInProject())
    print('(id - name) usuarios de un proyecto con un rol: ', p.listUsersInProjectRol(p.idRol(rol)))
    print('(id - name) grupos de un proyecto con un rol: ', p.listGroupsInProjectRol(p.idRol(rol)))
    print('verifica que usuario "{}" exista con rol en proyecto :'.format(userExiste), p.chkUserInProjectRol(p.idUser(userExiste), p.idRol(rol)))
    print('verifica que usuario "{}" NO exista con rol "{}" en proyecto:'.format(userNoExiste, rol), p.chkUserInProjectRol(p.idUser(userNoExiste), p.idRol(rol)))

    pr = p.objProject()
    print('verifica si tipo de petición "{}" pertenece al proyecto "{}":'.format(track, pr.name),p.chkTrackerInProject(p.idTracker(track)))

    print('usuario Nombre en proyecto', p.checkUserNameInProject('Luis Cibils'))
    print('usuario Id en proyecto', p.checkUserIdInProject(p.idUser('Luis Cibils')))
