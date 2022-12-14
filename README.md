# Composite
This is the microservice api of middleware for back-end. 
Request bodies from microservices of Course, Contact and Student are passed to Composite through HTTP protocols.
Here an address of a student will be verified when being added or edited.
User login and authentication is also merged into the middleware.

## API Communication Microservices
### Create
- /api/students/add
- /api/contacts/\<uni\>/add/\<type\>
- /api/courses/new_section
- /api/courses/\<call_no\>/new_project

### Read
- /api/students/get/\<uni\>
- /api/students/all
- /api/courses/\<call_no\>/projects/\<project_id\>/available_students
- /api/contacts/\<uni\>/\<type\>
- /api/contacts/\<type\>
- /api/contacts/\<uni\>
- /api/contacts/all
- /api/courses/all_sections
- /api/courses/\<call_no\>
- /api/courses/all_projects
- /api/courses/\<call_no\>/projects/\<project_id\>

### Update
- /api/students/update/\<uni\>
- /api/contacts/\<uni\>/update/\<type\>
- /api/courses/\<call_no\>
- /api/courses/\<call_no\>/projects/\<project_id\>

### Delete
- /api/students/delete/\<call_no\>/\<uni\>
- /api/contacts/\<uni\>/del/\<type\>/\<note\>
- /api/courses/\<call_no\>
- /api/courses/\<call_no\>/projects/\<project_id\>