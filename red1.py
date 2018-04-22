#!/usr/bin/python

from redminelib import Redmine
import datetime

'''
from pprint import pprint

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))
'''

#redmine = Redmine('https://colo1.msp.gub.uy/redmine/', key='3278578df5ce4f8f08e5907112dd4a4d5f7e9d97')
redmine = Redmine('https://colo1.msp.gub.uy/redmine/', key='7912b4cc1a85bbc3f0f8637bac2329d80a1a66a9')

def idProject(name):
    '''
        :param name:
        :return: Devuelve el id del proyecto o False si no existe
    '''
    projects = redmine.project.all()
    try:
        p = [x for x in projects if x.name == name][0]
        return p.id, p
    except:
        return False

def idTracker(name):
    '''
        :param name:
        :return: Devuelve el id del tipo de petición o False si no existe
    '''
    trackers = redmine.tracker.all()
    try:
        t = [x for x in trackers if x.name == name][0]
        return t.id
    except:
        return False

def idStatus(name):
    '''
        :param name:
        :return: Devuelve el id del estado o False si no existe
    '''
    statuses = redmine.issue_status.all()
    try:
        s = [x for x in statuses if x.name == name][0]
        return s.id
    except:
        return False

def categoryProject(project):
    '''
        :param project:
        :return: Devuelve la lista de id y nombre de las categorías del proyecto
    '''
    return [(x.id, x.name) for x in project.issue_categories]

def idCategory(project, name):
    '''
        :param name:
        :return: Devuelve el id de la categoría o False si no existe
    '''
    categories = redmine.issue_category.filter(project_id=project)
    try:
        c = [x for x in categories if x.name == name][0]
        return c.id
    except:
        return False
    
def trackerProject(project):
    '''
        :param project:
        :return: Devuelve la lista de id y nombre de las trackers del proyecto
    '''
    return [(x.id, x.name) for x in project.trackers]

def idPriority(name):
    '''
        :param name:
        :return: Devuelve el id de la prioridad o False si no existe
    '''
    priority = redmine.enumeration.filter(resource='issue_priorities')
    try:
        p = [x for x in priority if x.name == name][0]
        return p.id
    except:
        return False

def idUser(user):
    '''
        :param name:
        :return: Devuelve el id del usuario o False si no existe
    '''
    try:
        users = redmine.user.filter(name=user)
        return users[0].id
    except:
        return True

def idRol(name):
    '''
        :param name:
        :return: Devuelve el id del rol o False si no existe
    '''
    roles = redmine.role.all()
    try:
        r = [x for x in roles if x.name == name][0]
        return r.id
    except:
        return False

def userInProject(user, project):
    '''
        :param user:
        :param project:
        :return: Devuelve True o False según si el usuario pertenece o no al proyecto
    '''
    m = project.memberships
    return any(user == x.user['name'] for x in m if hasattr(x, 'user'))
    #return set([(x.user['id'], x.user['name']) for x in m for y in x.roles if y.id == rol and hasattr(x, 'user')])
def usersProjectRol(project, rol):
    '''
        :param project:
        :param rol:
        :return: Lista id y nombre de todos los usuarios de un proyecto que tienen un rol determinado
    '''
    m = project.memberships
    return set([(x.user['id'], x.user['name']) for x in m for y in x.roles if y.id == rol and hasattr(x, 'user')])

def groupsProjectRol(project, rol):
    '''
        :param project:
        :param rol:
        :return: Lista id y nombre de todos los grupos de usuarios de un proyecto que tienen un rol determinado
    '''
    m = project.memberships
    return set([(x.group['id'], x.group['name']) for x in m for y in x.roles if y.id == rol and hasattr(x, 'group')])

def chkUserProjectRol(user, project, rol):
    '''
        :param user: id or name
        :param project:
        :param rol:
        :return: Verifica que un usuario pertenezca a un proyecto en un determinado rol
    '''
    u = usersProjectRol(project, rol)
    t = 0 if isinstance(user, int) else 1 # si user es int, el parámetro es el id, de lo contrario es el nombre
    return user in [x[t] for x in u]

def chkTrackerProject(tracker, project):
    '''
        :param tracker: name
        :param project:
        :return: Verifica, por nombre, que el tipo de petición pertenezca a un proyecto
    '''
    t = 0 if isinstance(tracker, int) else 1
    return tracker in [x.id for x in project.trackers]

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
    
    p, project = idProject(proj)
    
    print('id project: ', p)
    print('id tracker: ', track)
    print('id status:', idStatus(status))
    print('id category:', idCategory(p, category))
    print('id user:', idUser(user))
    print('id priority:', idPriority(priority))
    print('id rol:', idRol(rol))
    print('categorias de un proyecto: ', categoryProject(project))
    print('tipos de petición de un proyecto: ', trackerProject(project))
    print('(id - name) usuarios de un proyecto con un rol: ', usersProjectRol(project, idRol(rol)))
    print('(id - name) grupos de un proyecto con un rol: ', groupsProjectRol(project, idRol(rol)))
    print('verifica que usuario "{}" exista con rol en proyecto :'.format(userExiste), chkUserProjectRol(userExiste, project, idRol(rol)))
    print('verifica que usuario "{}" NO exista con rol en proyecto:'.format(user), chkUserProjectRol(userExiste, project, idRol(rol)))
    print('verifica si petición {} pertenece al proyecto {}:'.format(track, project), chkTrackerProject(track, project))
    print('usuario en proyecto', userInProject('Luis Cibils', project))
'''
projects = redmine.project.all()
trackers = redmine.tracker.all()

p = [x for x in projects if x.name == proj][0]
print('project', list(p))

t = [x for x in trackers if x.name == track][0]
print('track', list(t))

categories = redmine.issue_category.filter(project_id=p.id)
print(list(categories[0]))


for c in categories:
    print(c.id, c.name)

#print(list(redmine.project.get(p.id)))

users = redmine.user.filter(name=user)
print(list(users[0]))

groups = redmine.group.all()

print(list(groups[1]))
#print(len(p.memberships))
#membership = redmine.project_membership.get(p.id)
memberships = redmine.project_membership.filter(project_id=p.id)
for x in memberships: # miembros del proyecto p.id
    print(list(x))
#m = [x for x in memberships if x.user.name == user][0]

#print(list(redmine.project.get(p.id)))
print('memberships: ', list(memberships[0]))
g = [x for x in groups if x.id == memberships[0].group['id'] ] # los grupos de
print(list(g[0]))
'''

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
