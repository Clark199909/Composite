from src.resources.items_getting import email_getting

class StudentProcessing:
    def __int__(self):
        pass

    @staticmethod
    def processing(students_content, courses_content):
        info_list = []
        for record in students_content:
            uni = record['uni']
            email = email_getting(uni)
            courses_record = courses_content[uni]
            info = {
                'uni': uni,
                'name': record['first_name'] + ', ' + record['last_name'],
                'nationality': record['nationality'],
                'race': record['race'],
                'gender': record['gender'],
                'admission_date': record['admission_date'],
                'call_no': courses_record['call_no'],
                'project_id': courses_record['project_id'],
                'project_name': courses_record['project_name'],
                'team_name': courses_record['team_name'],
                'section_period': courses_record['section_period']
            }
            info_list.append(info)
        return info_list

