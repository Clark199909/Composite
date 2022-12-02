from src.resources.items_getting import name_getting

class ContactProcessing:
    def __int__(self):
        pass

    @staticmethod
    def address_processing(content):
        """ getting addresses of certain uni
            returns a list of addresses in the format we want for frontend
        """
        addr_list = []
        for record in content:
            id = record['id']
            uni = record['uni']
            name = name_getting(uni)
            type = record['address_type']
            address = record['street'] + ', ' + record['city'] + ', ' + record['state'] + ', ' + record[
                'country'] + ', ' + record['zip_code']
            addr_list.append({'id': id,
                              'uni': uni,
                              'name': name,
                              'type': 'address',
                              'note': type,
                              'content': address})
        return addr_list

    @staticmethod
    def phone_processing(content):
        """ getting phones of certain uni
            returns a list of phones in the format we want for frontend
        """
        phone_list = []
        for record in content:
            id = record['id']
            uni = record['uni']
            name = name_getting(uni)
            type = record['phone_type']
            phone = record['country_code'] + ' ' + record['phone_no']
            phone_list.append({'id': id,
                               'uni': uni,
                               'name': name,
                               'type': 'phone',
                               'note': type,
                               'content': phone})
        return phone_list

    @staticmethod
    def email_processing(content):
        """ getting emails of certain uni
            returns a list of emails in the format we want for frontend
        """
        email_list = []
        for record in content:
            id = record['id']
            uni = record['uni']
            name = name_getting(uni)
            type = record['email_type']
            email = record['address']
            email_list.append({'id': id,
                               'uni': uni,
                               'name': name,
                               'type': 'email',
                               'note': type,
                               'content': email})
        return email_list

    @staticmethod
    def processing(type, content):
        if type == 'address':
            return ContactProcessing.address_processing(content)
        elif type == 'phone':
            return ContactProcessing.phone_processing(content)
        elif type == 'email':
            return ContactProcessing.email_processing(content)

