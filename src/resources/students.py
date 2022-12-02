from src.resources.items_getting import email_getting

class StudentProcessing:
    def __int__(self):
        pass

    @staticmethod
    def processing(content):
        info_list = []
        for record in content:
            uni = record['uni']
            email = email_getting(uni)
            info = {
                'uni': uni,
                'name': record['first_name'] + ', ' + record['last_name'],
                'nationality': record['nationality'],
                'ethnicity': record['ethnicity'],
                'gender': record['gender'],
                'admission_date': record['admission_date'],
                'email': email
            }
            info_list.append(info)
        return info_list

