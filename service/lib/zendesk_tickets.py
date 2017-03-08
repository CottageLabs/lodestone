from zdesk import Zendesk, get_id_from_url
from octopus.core import app
from service.lib.crud_helper import CrudHelper


# Reference:
#   https://github.com/fprimex/zdesk
#   https://github.com/fprimex/zdesk/blob/master/zdesk/zdesk_api.py
#   https://developer.zendesk.com/rest_api/docs/core/tickets#create-ticket
#   https://developer.zendesk.com/rest_api/docs/core/ticket_forms#list-ticket-forms

class ZendeskTickets:
    def __init__(self, model, job_id):

        url = app.config.get('ZENDESK_URL')
        un = app.config.get('ZENDESK_USERNAME')
        pw = app.config.get('ZENDESK_PASSWORD')
        token = app.config.get("ZENDESK_TOKEN")
        if token is not None:
            self.zen = Zendesk(url, zdesk_email=un, zdesk_password=token, zdesk_token=True)
        else:
            self.zen = Zendesk(url, zdesk_email=un, zdesk_password=pw)

        self.data_form_fields = app.config.get('ZENDESK_DATA_FORM_FIELDS')
        self.thesis_form_fields = app.config.get('ZENDESK_THESIS_FORM_FIELDS')
        self.job_id = job_id
        self.model = model
        self.dao = CrudHelper(model, job_id=job_id)
        self.record = self.dao.get_record()
        self.requester_name = app.config.get('ZENDESK_TICKET_REQUESTER_NAME')
        self.requester_email = app.config.get('ZENDESK_TICKET_REQUESTER_EMAIL')
        if self.record and self.record.get('user_auth', None):
            if self.record['user_auth'].get('name', None):
                self.requester_name = self.record['user_auth']['name']
            if self.record['user_auth'].get('email', None):
                self.requester_email = self.record['user_auth']['email']
        return

    def create_dataset_ticket(self):
        custom_fields = []

        if self.record.get('id', None):
            custom_fields.append({
                'id': self.data_form_fields['field_external_id'],
                'value': self.record['id']
            })
        if self.record.get('confidential_information', None) is not None:
            custom_fields.append({
                'id': self.data_form_fields['field_confidential_information'],
                'value': self.record['confidential_information']
            })
        if self.record.get('doi', None):
            custom_fields.append({
                'id': self.data_form_fields['field_doi'],
                'value': self.record['doi']
            })
        if self.record.get('has_publication', None) is not None:
            custom_fields.append({
                'id': self.data_form_fields['field_supporting_publication'],
                'value': self.record['has_publication']
            })
        if self.record.get('publicationtitle', None):
            custom_fields.append({
                'id': self.data_form_fields['field_manuscript_title'],
                'value': self.record['publicationtitle']
            })
        if self.record.get('journal_name', None):
            custom_fields.append({
                'id': self.data_form_fields['field_journal_title'],
                'value': self.record['journal_name']
            })
        if self.record.get('publication_date', None):
            custom_fields.append({
                'id': self.data_form_fields['field_publication_date'],
                'value': self.record['publication_date']
            })
        if self.record.get('iscitedby', None):
            custom_fields.append({
                'id': self.data_form_fields['field_article_link'],
                'value': self.record['iscitedby']
            })
        if self.record.get('publication_published', None) is not None:
            custom_fields.append({
                'id': self.data_form_fields['field_published'],
                'value': self.record['publication_published']
            })
        if self.record.get('peerreviewaccess', None) is not None:
            custom_fields.append({
                'id': self.data_form_fields['field_accessible_to_peerreviewers'],
                'value': self.record['peerreviewaccess']
            })
        if self.record.get('embargo', None) is not None:
            custom_fields.append({
                'id': self.data_form_fields['field_dataset_embargoed'],
                'value': self.record['embargo']
            })
        if self.record.get('publicise', None) is not None:
            custom_fields.append({
                'id': self.data_form_fields['field_promote_on_twitter'],
                'value': self.record['publicise']
            })
        if self.record.get('twitter', None):
            custom_fields.append({
                'id': self.data_form_fields['field_twitter_handle'],
                'value': self.record['twitter']
            })
        if self.record.get('additionalinfo', None):
            custom_fields.append({
                'id': self.data_form_fields['field_additional_information'],
                'value': self.record['additionalinfo']
            })
        if self.record.get('placeholder', None) is not None:
            custom_fields.append({
                'id': self.data_form_fields['field_placeholder_dataset'],
                'value': self.record['placeholder']
            })
        if self.record.get("title", None) is not None:
            custom_fields.append({
                "id" : self.data_form_fields["field_title"],
                "value" : self.record["title"]
            })

        new_ticket = {
            'ticket': {
                'requester': {
                    'name': self.requester_name,
                    'email': self.requester_email,
                },
                'subject': 'New submission %s' % self.record['id'],
                'description': self.record['description'],
                'ticket_form_id': self.data_form_fields['ticket_form_id'],
                'group_id': self.data_form_fields['ticket_group_id'],
                'custom_fields': custom_fields
            }
        }

        result = self.zen.ticket_create(data=new_ticket)
        if result is None:
            return False
        ticket_id = get_id_from_url(result)
        if ticket_id:
            self.dao.dao_record.ticket_id = ticket_id
            self.dao.dao_record.save()
        return True

    def update_dataset_ticket(self):
        if self.record.get('ticket_id', None) is None:
            return False
        custom_fields = []
        if self.record.get('doi', None):
            custom_fields.append({'id': self.data_form_fields['field_doi'], 'value': self.record['doi']})
        else:
            return True
        data_to_update = {
            'ticket': {
                'custom_fields': custom_fields
            }
        }
        result = self.zen.ticket_update(self.record['ticket_id'], data_to_update)
        if result is None:
            return False
        return True

    def create_ethesis_ticket(self):
        custom_fields = []
        if self.record.get('id', None):
            custom_fields.append({
                'id': self.thesis_form_fields['field_external_id'],
                'value': self.record['id']
            })
        crsids = []
        email_ids = []
        for a in self.record['authors']:
            if a.get('crsid', None):
                crsids.append(a['crsid'])
            if a.get('email_id', None):
                email_ids.append(a['email_id'])
        crsids = ', '.join(crsids)
        email_ids = ', '.join(email_ids)
        if crsids:
            custom_fields.append({
                'id': self.thesis_form_fields['field_crsid'],
                'value': crsids
            })
        if email_ids:
            custom_fields.append({
                'id': self.thesis_form_fields['field_external_email_address'],
                'value': email_ids
            })
        if self.record.get('awarding_institution', None):
            custom_fields.append({
                'id': self.thesis_form_fields['field_awarding_institution'],
                'value': self.record['awarding_institution']
            })
        if self.record.get('college', None):
            custom_fields.append({
                'id': self.thesis_form_fields['field_college'],
                'value': self.record['college']
            })
        if self.record.get('faculty', None):
            custom_fields.append({
                'id': self.thesis_form_fields['field_department'],
                'value': self.record['faculty']
            })
        # qualification_level
        val = None
        if self.record.get('qualification_level', None):
            if 'Doctoral' in self.record['qualification_level']:
                val = "qualification_level_doctoral"
            elif 'Higher Doctorate' in self.record['qualification_level']:
                val = "qualification_level_higher_doctorate"
            elif 'Masters' in self.record['qualification_level']:
                val = "qualification_level_masters"
            elif 'Other Postgraduate' in self.record['qualification_level']:
                val = "qualification_level_other_postgraduate"
        if val:
            custom_fields.append({
                'id': self.thesis_form_fields['field_qualification_level'],
                'value': val
            })
        if self.record.get('degree', None):
            custom_fields.append({
                'id': self.thesis_form_fields['field_degree'],
                'value': self.record['degree']
            })
        if self.record.get('degree_title', None) is not None:
            custom_fields.append({
                'id': self.thesis_form_fields['field_degree_title'],
                'value': self.record['degree_title']
            })
        if self.record.get('title', None):
            custom_fields.append({
                'id': self.thesis_form_fields['field_thesis_title'],
                'value': self.record['title']
            })
        if self.record.get('date_awarded', None):
            custom_fields.append({
                'id': self.thesis_form_fields['field_date_awarded'],
                'value': self.record['date_awarded']
            })
        if self.record.get('funding', None):
            custom_fields.append({
                'id': self.thesis_form_fields['field_funders'],
                'value': self.record['funding']
            })
        # thesis access level
        val = None
        if self.record.get('access', None) and self.record['access'].get('type', None):
            if 'none' in self.record['access']['type']:
                val = "thesis_access_level_open_access"
            elif 'one' in self.record['access']['type']:
                val = "thesis_access_level_1_year_embargo"
            elif 'two' in self.record['access']['type']:
                val = "thesis_access_level_2_year_embargo"
            elif 'indefinite' in self.record['access']['type']:
                val = "thesis_access_level_indefinite_embargo"
        if val:
            custom_fields.append({
                'id': self.thesis_form_fields['field_thesis_access_level'],
                'value': val
            })
        # licence
        val = None
        if self.record.get('license', None) and self.record['license'].get('text', None):
            if 'All rights reserved' in self.record['license']['text']:
                val = "all_rights_reserved"
            elif 'CC BY-NC-ND' in self.record['license']['text']:
                val = "cc_by_nc_nd"
            elif 'CC BY-NC-SA' in self.record['license']['text']:
                val = "cc_by_nc_sa"
            elif 'CC BY-ND' in self.record['license']['text']:
                val = "cc_by_nd"
            elif 'CC BY-NC' in self.record['license']['text']:
                val = "cc_by_nc"
            elif 'CC BY-SA' in self.record['license']['text']:
                val = "cc_by_sa"
            elif 'CC BY' in self.record['license']['text']:
                val = "cc_by"
        if val:
            custom_fields.append({
                'id': self.thesis_form_fields['field_licence'],
                'value': val
            })

        new_ticket = {
            'ticket': {
                'requester': {
                    'name': self.requester_name,
                    'email': self.requester_email,
                },
                'subject': 'New submission %s' % self.record['id'],
                'description': self.record['abstract'],
                'ticket_form_id': self.thesis_form_fields['ticket_form_id'],
                'group_id': self.thesis_form_fields['ticket_group_id'],
                'custom_fields': custom_fields
            }
        }

        if self.record.get("ticket_id") is not None:
            # this means that a ticket was already created, possibly in some previous erroneous attempt to
            # deposit the item
            result = self.zen.ticket_update(self.record["ticket_id"], new_ticket)
            if result is None:
                return False
        else:
            result = self.zen.ticket_create(data=new_ticket)
            if result is None:
                return False

            ticket_id = get_id_from_url(result)
            if ticket_id:
                self.dao.dao_record.ticket_id = ticket_id
            self.dao.dao_record.save()

        return True

    def get_ticket(self):
        if self.record.get('ticket_id', None):
            return False
        result = self.zen.ticket_show(self.record['ticket_id'])
        return result

    def list_tickets_per_page(self):
        # To get a ;list of all tickets
        tickets = self.zen.tickets_list()
        # u'tickets', u'count', u'next_page', u'previous_page']
        # tickets['count']
        # tickets['tickets']
        return tickets

    def list_ticket_fields_per_page(self):
        ticket_fields = self.zen.ticket_fields_list()
        print ticket_fields.keys()
        # [u'count', u'next_page', u'ticket_fields', u'previous_page']
        return ticket_fields

    def list_forms_per_page(self):
        ticket_forms = self.zen.ticket_forms_list()
        # print ticket_forms.keys()
        for f in ticket_forms['ticket_forms']:
            print f['name']
            print f['url']
            print f['id']
            print f['ticket_field_ids']
            print f['created_at']
            print f['updated_at']
            print '-' * 60
        # [u'count', u'next_page', u'ticket_forms', u'previous_page']
        return ticket_forms

    def get_form(self, form_id):
        form = self.zen.ticket_form_show(form_id)
        return form

    def get_field(self, field_id):
        field = self.zen.ticket_field_show(field_id)
        return field
