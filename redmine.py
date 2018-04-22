#!/usr/bin/python

from redminelib import Redmine
import datetime

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
        self.fields = {
            'Asunto': '*',
            'Descripción': '*',
            'Estado': '*id:status',
            'Prioridad': '*id:priority',
            'Asignado a': '-id:user',
            'Categoría': '*id:category',
            'Fecha de inicio': '',
            'Checklist': '',
            'Ficheros': ''
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

    def checkFieldIsValid(self, fieldName):
        return fieldName in dict.keys(self.fields)

    def checkValueisValidField(self, field, value):
        v = self.fields.get(field) # toma el valor asociado al parametro 'field' en el dict 'fields'
        msg = 'Ok'
        r = True
        if v == '*':
            if value == '':
                msg = 'Required'
                r = False
        elif v[1:3] == 'id': # value not required but if exists must be in the list
            if value == '':
                if v[0] == '-':
                    r = True
                else:
                    msg = 'Required'
                    r = False
            else: # value not null, must be in the list
                f = v[4:]
                if f == 'status':
                    r = self.idStatus(value)
                elif f == 'category':
                    r = self.idCategory(value)
                elif f == 'user':
                    idU = self.idUser(value)
                    if idU:
                        r = self.checkUserIdInProject(idU)
                    else:
                        r = False
                elif f == 'priority':
                    r = self.idPriority(value)
                if not r:
                    msg = 'Value not valid'
        return r, msg

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

    def idTracker(self, trackerName):
        '''
            :param trackerName: Nombre del tipo de petición
            :return: Devuelve el id del tipo de petición o False si no existe
        '''
        if not self.trackers:
            self.trackers = self.redmine.tracker.all()
        try:
            self.tracker = [x for x in self.trackers if x.name == trackerName][0]
            return self.tracker.id
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

    def listCategoriesInProject(self):
        '''
            :return: Devuelve la lista de id y nombre de las categorías del proyecto
        '''
        return [(x.id, x.name) for x in self.project.issue_categories]

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

    def listTrackersInProject(self):
        '''
            :return: Devuelve la lista de id y nombre de los tipos de petición del proyecto
        '''
        return [(x.id, x.name) for x in self.project.trackers]

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

    def composeCustomFields(self, *args):
        '''
        Compose a dict with: custom_fields = [{'id': 1, 'value': 'foo'}, {'id': 2, 'value': 'bar'}]
        :param args:
        :return:
        '''

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
        if 'watcher_user_ids' in fieldsDict and fieldsDict['watcher_user_ids'] != '':
            issue.watcher_user_ids = fieldsDict['watcher_user_ids']
        if 'parent_issue_id' in fieldsDict and fieldsDict['parent_issue_id'] != '':
            issue.parent_issue_id = fieldsDict['parent_issue_id']
        if 'Fecha de inicio' in fieldsDict and fieldsDict['Fecha de inicio'] != '':
            issue.start_date = fieldsDict['start_date']
        if 'Fecha fin' in fieldsDict and fieldsDict['Fecha fin'] != '':
            issue.due_date = fieldsDict['due_date']
        if 'estimated_hours' in fieldsDict and fieldsDict['estimated_hours'] != '':
            issue.estimated_hours = fieldsDict['estimated_hours']
        if 'done_ratio' in fieldsDict and fieldsDict['done_ratio'] != '':
            issue.done_ratio = fieldsDict['done_ratio']
        if 'custom_fields' in fieldsDict and fieldsDict['custom_fields'] != '':
            issue.custom_fields = fieldsDict['custom_fields']
        if 'Ficheros' in fieldsDict and fieldsDict['Ficheros'] != '':
            issue.uploads =  [{'path': fieldsDict['Ficheros']}]
        issue.save()
        return

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



'''
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
#print('len de g', len(g))
'''
#fields = redmine.custom_field.all()
print(dir(fields[0]))
for c in fields:
    print(c.id, c.name)
#print([(c.id) for c in categories])
enumerations = redmine.enumeration.filter(resource='time_entry_activities')
#pprint(vars(trackers))
for p in projects:
    if p.name == proj:
        break



print(p.name, p.id)
print(t.name, t.id)
#print(t.__dict__)
#print(p.__dict__)

#print(p.issues[0].__dict__)


#print(p.trackers.__dict__)


print(p.issues[0].assigned_to)
print('custom fields: \n',dir(p.issues[0].custom_fields.values_list))

#dump(trackers[0])
pId = [p.id for p in projects if p.name == proy][0]
#print(pId)
#print(projects[84].__dict__)
#pcf = [p.issue_custom_field_ids for p in projects if p.name == proy][0]
#tids = [p.tracker_ids for p in projects if p.name == proy][0]
#print(list(tids))
#print(pcf[0].id, pcf[0].name)
print('Proyecto id: ', pId)
#print([(i.id, i.name, '\t') for i in trackers])

tId = [t.id for t in trackers if t.name == tipo][0]
print('Tipo Petición id: ', tId)



#fields = redmine.custom_field.all()

#print([(i.id, i.name) for i in fields])
#dump(campos)
'''
'''
print(list(redmine.project.get(pid)))
print(redminelib.managers.ResourceManager.get(pid, include='trackers,issue_categories,enabled_modules,time_entry_activities'))
#print(tracker_ids)
'''
'''
p = redmine.project.get('aprobacion')
#print(repr(list(p)))
issues = redmine.issue.filter(project_id=2)
'''
'''
for issue in issues:
    print(issue.id)
    print(list(issue))
'''
'''
memberships = redmine.project_membership.filter(project_id=22)
for ms in memberships:
    print(list(ms))
    print(ms.user)
#'''
'''
from io import StringIO
issue = redmine.issue.create(
    project_id='2',
    subject='petición automática',
    tracker_id=4,
    description='Descripción de petición creada automáticamente con biblioteca redmine-python\otra línea',
    status_id=3,
    priority_id=2,
    author_id=11,
    custom_fields=[{'id': 37, 'value': '2018-03-05'}]

)

print(list(issue))
'''
'''
    uploads=[{'path': 'C:\\Users\\Usuario\\PycharmProjects\\proyEE\\carpetaPDF\\ProcesadosOK\\NUEVA PALMIRA 2018-28-1-015646.pdf'},
        {'path': 'I am content of file 2'}]
'''
'''
map = {
    subject (string) – (required). Issue subject.
    tracker_id (int) – (optional). Issue tracker id.
    'description': 'Descripción'
    status_id (int) – (optional). Issue status id.
    priority_id (int) – (optional). Issue priority id.
    category_id (int) – (optional). Issue category id.
    fixed_version_id (int) – (optional). Issue version id.
    is_private (bool) – (optional). Whether issue is private.
    assigned_to_id (int) – (optional). Issue will be assigned to this user id.
    watcher_user_ids (list) – (optional). User ids watching this issue.
    parent_issue_id (int) – (optional). Parent issue id.
    start_date (string or date object) – (optional). Issue start date.
    due_date (string or date object) – (optional). Issue end date.
    estimated_hours (int) – (optional). Issue estimated hours.
    done_ratio (int) – (optional). Issue done ratio.
    custom_fields (list) – (optional). Custom fields as [{‘id’: 1, ‘value’: ‘foo’}].
    uploads (list) – (optional). Uploads as [{'': ''}, ...], accepted keys are:
    path (required). Absolute file path or file-like object that should be uploaded.
    filename (optional). Name of the file after upload.
    description (optional). Description of the file.
    content_type (optional). Content type of the file.
}
'''
'''
m = {
    'a': 'a1',
    'b': 'b1',
    'c': 'c1'
}

l = ['a1', 'c1']
r =[] # contendrá la lisa de variables de cada columna
for i in l:
    if i in m.values():
        r.append(list(m.keys())[list(m.values()).index(i)])
    else:
        print('error')
        break
print(r)

categories = redmine.issue_category.filter(project_id=p.Id)
print(dir(categories[0]))
for c in categories:
    print(c.id, c.name)
#print([(c.id) for c in categories])
'''


'''
from pprint import pprint

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))
'''


'''       
            
            if not rm.checkValueisValidField(v[3:], cell):
                log.info('La celda [{}, {}] = "{}" no tiene un valor válido de "{}"'.format(i, j, cell, v[3:]))
                r = False
        if field == 'status':
            return self.idStatus(value)
        elif field == 'category':
            return self.idCategory(value)
        elif field == 'user':
            idU = self.idUser(value)
            if idU:
                return self.checkUserIdInProject(idU)
            else:
                False
        elif field == 'priority':
            return self.idPriority(value)

'''
