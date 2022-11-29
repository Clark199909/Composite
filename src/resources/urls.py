# TODO consider using config or db to get these urls
__urls = {'students': 'http://127.0.0.1:5012',
          'courses': 'http://127.0.0.1:5013',
          'contacts': 'http://127.0.0.1:5014',
          }

def get_students_url():
    return __urls['students']

def get_courses_url():
    return __urls['courses']

def get_contacts_url():
    return __urls['contacts']