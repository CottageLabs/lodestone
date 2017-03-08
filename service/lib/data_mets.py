from xml.etree.ElementTree import Element, SubElement, Comment, tostring, register_namespace
from xml.dom import minidom
from datetime import datetime
import os, codecs


class DataMets:
    def __init__(self, data):
        self.terms = {
            'type': {'mdschema': 'dc', 'element': 'type'},
            'accessrights': {'mdschema': 'dcterms', 'element': 'accessrights'},
            'publicationtitle': {'mdschema': 'cam', 'element': 'data', 'qualifier': 'publicationtitle'},
            'iscitedbydoi': {'mdschema': 'datacite', 'element': 'iscitedby', 'qualifier':'doi'},
            'iscitedbyurl': {'mdschema': 'datacite', 'element': 'iscitedby', 'qualifier':'url'},
            'title': {'mdschema': 'dc', 'element': 'title'},
            'author_names': {'mdschema': 'dc', 'element': 'contributor', 'qualifier': 'author'},
            'author_orcids': {'mdschema': 'dc', 'element': 'contributor', 'qualifier': 'orcid'},
            'supervisor_names': {'mdschema': 'datacite', 'element': 'contributor', "qualifier" : "supervisor"},
            'description': {'mdschema': 'dc', 'element': 'description'},
            'keywords': {'mdschema': 'dc', 'element': 'subject'},
            'resources_webpage': {'mdschema': 'cam', 'element': 'relation', 'qualifier': 'webpage'},
            'resources_sourcecode': {'mdschema': 'cam', 'element': 'relation', 'qualifier': 'sourcecode'},
            'resources_otherpublication': {'mdschema': 'cam', 'element': 'relation', 'qualifier': 'otherpublication'},
            'resources_conferenceoutput': {'mdschema': 'cam', 'element': 'relation', 'qualifier': 'conferenceoutput'},
            'resources_otherdataset': {'mdschema': 'cam', 'element': 'relation', 'qualifier': 'otherdataset'},
            'resources_report': {'mdschema': 'cam', 'element': 'relation', 'qualifier': 'report'},
            'resources_blog': {'mdschema': 'cam', 'element': 'relation', 'qualifier': 'blog'},
            'resources_other': {'mdschema': 'cam', 'element': 'relation', 'qualifier': 'other'},
            'funder_project_id': {'mdschema': 'pubs', 'element': 'funder-project-id'},
            'submitter': {'mdschema': 'cam', 'element': 'data', 'qualifier': 'submitter'},
            'department': {'mdschema': 'dc', 'element': 'publisher', 'qualifier': 'department'},
            'crsid': {'mdschema': 'pubs', 'element': 'staff-id'},
            'externalemail': {'mdschema': 'cam', 'element': 'externalEmail'},
            'additionalinfo': {'mdschema': 'cam', 'element': 'data', 'qualifier': 'info'},
            'license_text': {'mdschema': 'dc', 'element': 'rights'},
            'license_uri': {'mdschema': 'dc', 'element': 'rights', 'qualifier': 'uri'},
            'twitter': {'mdschema': 'cam', 'element': 'twitter'},
            "author" : {"mdschema" : "dc", "element" : "contributor", "qualifier" : "author"},
            "orcid" : {"mdschema" : "dc", "element" : "contributor", "qualifier" : "orcid"},
            "format" : {"mdschema" : "dc", "element" : "format"},
            "software_information" : {"mdschema" : "dc", "element" : "format"}
        }

        # Form metadata not used
        # external_funding
        # confidential_information
        # confirm_sharing_rights
        # placeholder
        # has_publication
        # journal_name
        # publication_published
        # embargo (embargo_yes / embargo_no)
        # publication_date
        # supervisor_orcids
        # currently_employed (currently_employed_yes / currently_employed_no)
        # publicise (publicise_yes / publicise_no)
        # terms_and_conditions

        self.admin_files = [data["id"] + '_confirmations.txt']

        register_namespace('xlink', 'http://www.w3.org/1999/xlink')
        register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        register_namespace('dim', 'http://www.dspace.org/xmlns/dspace/dim')
        register_namespace('', 'http://www.loc.gov/METS/')
        register_namespace('premis', 'http://www.loc.gov/standards/premis')
        register_namespace('rights', 'http://cosimo.stanford.edu/sdr/metsrights/')
        self.data = data
        self.id = self.data['id']
        self.flatten_data()
        self.mets = Element('{http://www.loc.gov/METS/}mets', {
            'ID': "data_mets",
            'OBJID': self.id,
            'TYPE': 'DSPace ITEM',
            'PROFILE': 'DSpace METS SIP Profile 1.0',
            '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation':
                'http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd'
        })
        self.amdsec = None
        return

    def save_xml(self):
        file_path = os.path.join(self.data['dir'], 'mets.xml')
        if not os.path.exists(self.data['dir']):
            os.makedirs(self.data['dir'])
        mets_xml = self.xml()
        f = codecs.open(file_path, 'w', "utf-8")
        f.write(mets_xml)
        f.close()
        return file_path

    def xml(self):
        self.header()
        self.descriptive_metadata()
        self.admin_metadata()
        self.file_section_metadata()
        self.struct_metadata()
        return prettify(self.mets)

    def header(self):
        generated_on = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        header = SubElement(self.mets, 'metsHdr', {'CREATEDATE': generated_on})
        agent = SubElement(header, 'agent', {'ROLE': 'CREATOR', 'TYPE': 'OTHER',
                                             'OTHERTYPE': 'Lodestone'})
        name = SubElement(agent, 'name')
        name.text = 'Lodestone'
        return

    def descriptive_metadata(self):
        dmdsec = SubElement(self.mets, 'dmdSec', {'ID': 'dmdSec_1'})
        mdwrap = SubElement(dmdsec, 'mdWrap', {'MDTYPE': 'OTHER', 'OTHERMDTYPE': 'DIM'})
        xmldata = SubElement(mdwrap, 'xmlData')
        dim = SubElement(xmldata, '{http://www.dspace.org/xmlns/dspace/dim}dim', {'dspaceType': 'ITEM'})
        if not self.data.get('type', None):
            self.data['type'] = ['Dataset']
        for term, attributes in self.terms.iteritems():
            if not self.data.get(term, None):
                continue
            vals = self.data[term]
            if not isinstance(vals, list):
                vals = [vals]
            for val in vals:
                if not val:
                    continue
                fld = SubElement(dim, '{http://www.dspace.org/xmlns/dspace/dim}field', attributes)
                fld.text = unicode(val)
        return

    def admin_metadata(self):
        count = 1
        # content files
        for data_file in self.data['files']:
            if data_file['file_name'] in self.admin_files:
                continue
            self.amdsec = SubElement(self.mets, 'amdSec', {'ID': 'amdSec_%d' % count})
            self.file_tech_metadata(data_file, count)
            self.file_rights_metadata(data_file, count)
            self.file_source_metadata(data_file, count)
            count += 1
        # admin files
        for data_file in self.data['files']:
            if not data_file['file_name'] in self.admin_files:
                continue
            self.amdsec = SubElement(self.mets, 'amdSec', {'ID': 'amdSec_%d' % count})
            self.file_tech_metadata(data_file, count)
            self.file_rights_metadata(data_file, count, type='admin')
            self.file_source_metadata(data_file, count)
            count += 1
        return

    def file_section_metadata(self):
        count = 1
        filesec = SubElement(self.mets, 'fileSec')
        # content files
        filegrp1 = SubElement(filesec, 'fileGrp', {'ID': 'fileGrp_1', 'USE': 'CONTENT'})
        sequence = 1
        for data_file in self.data['files']:
            if data_file['file_name'] in self.admin_files:
                continue
            fileprop = SubElement(filegrp1, 'file', {
                'GROUPID': 'fileGrp_1',
                'ID': 'file_%d' % count,
                'MIMETYPE': data_file.get('file_mime_type', ''),
                'SEQ': '%d' % sequence,
                'ADMID': 'amdSec_%d' % count
            })
            SubElement(fileprop, 'FLocat', {'LOCTYPE': 'URL', '{http://www.w3.org/1999/xlink}href':
                                                                            data_file.get('file_name', '')})
            count += 1
            sequence += 1
        # admin files
        filegrp2 = SubElement(filesec, 'fileGrp', {'ID': 'fileGrp_2', 'USE': 'ADMIN'})
        # sequence = 1
        for data_file in self.data['files']:
            if not data_file['file_name'] in self.admin_files:
                continue
            fileprop = SubElement(filegrp2, 'file', {
                'GROUPID': 'fileGrp_2',
                'ID': 'file_%d' % count,
                'MIMETYPE': data_file.get('file_mime_type', ''),
                'SEQ': '%d' % sequence,
                'ADMID': 'amdSec_%d' % count
            })
            SubElement(fileprop, 'FLocat', {'LOCTYPE': 'URL', '{http://www.w3.org/1999/xlink}href':
                                                                            data_file.get('file_name', '')})
            count += 1
            sequence += 1
        return

    def struct_metadata(self):
        structmap = SubElement(self.mets, 'structMap', {'ID': 'structMap_1', 'LABEL': 'structure', 'TYPE': 'LOGICAL'})
        div = SubElement(structmap, 'div', {'ID': 'structMap_div_1', 'DMDID': 'dmdSec_1', 'TYPE': 'DSpace Object'})
        for count in range(1, len(self.data['files']) + 1):
            div2 = SubElement(div, 'div', {'ID': 'structMap_div_%d' % (count+1)})
            SubElement(div2, 'fptr', {'FILEID': 'file_%d' % count})
        return

    def file_tech_metadata(self, data_file, count):
        techmd = SubElement(self.amdsec, 'techMD', {'ID': 'techMD_%d' % count})
        mdwrap = SubElement(techmd, 'mdWrap', {'MDTYPE': 'PREMIS'})
        xmldata = SubElement(mdwrap, 'xmlData', {'{http://www.w3.org/2001/XMLSchema-instance}schemaLocation':
                                                 'http://www.loc.gov/standards/premis http://www.loc.gov/standards/premis/PREMIS-v1-0.xsd'})
        premis_premis = SubElement(xmldata, '{http://www.loc.gov/standards/premis}premis')
        premis_object = SubElement(premis_premis, '{http://www.loc.gov/standards/premis}object')
        premis_chr = SubElement(premis_object, '{http://www.loc.gov/standards/premis}objectCharacteristics')
        if data_file.get('file_fixity', None):
            premis_fixity = SubElement(premis_chr, '{http://www.loc.gov/standards/premis}fixity')
            premis_mda = SubElement(premis_fixity, '{http://www.loc.gov/standards/premis}messageDigestAlgorithm')
            premis_mda.text = data_file['file_fixity'].get('type', '')
            premis_digest = SubElement(premis_fixity, '{http://www.loc.gov/standards/premis}messageDigest')
            premis_digest.text = data_file['file_fixity'].get('value', '')
        if data_file.get('file_size', None):
            premis_size = SubElement(premis_chr, '{http://www.loc.gov/standards/premis}size')
            premis_size.text = unicode(data_file['file_size'])
        premis_format = SubElement(premis_chr, '{http://www.loc.gov/standards/premis}format')
        premis_fd = SubElement(premis_format, '{http://www.loc.gov/standards/premis}formatDesignation')
        premis_fn = SubElement(premis_fd, '{http://www.loc.gov/standards/premis}formatName')
        premis_fn.text = data_file.get('file_mime_type', '')
        premis_original_fn = SubElement(premis_object, '{http://www.loc.gov/standards/premis}originalName')
        premis_original_fn.text = data_file.get('file_name', '')
        return

    def file_rights_metadata(self, data_file, count, type=None):
        rightsmd = SubElement(self.amdsec, 'rightsMD', {'ID': 'rightsMD_%d' % count})
        mdwrap = SubElement(rightsmd, 'mdWrap', {'MDTYPE': 'OTHER', 'OTHERMDTYPE': 'METSRIGHTS'})
        xmldata = SubElement(mdwrap, 'xmlData', {'xsi:schemaLocation':
           'http://cosimo.stanford.edu/sdr/metsrights/ http://cosimo.stanford.edu/sdr/metsrights.xsd'})
        declaration = SubElement(xmldata, '{http://cosimo.stanford.edu/sdr/metsrights/}RightsDeclarationMD',
                                 {'RIGHTSCATEGORY': 'LICENSED'})
        if type == 'admin':
            context = SubElement(declaration, '{http://cosimo.stanford.edu/sdr/metsrights/}Context',
                                 {'CONTEXTCLASS': 'GENERAL PUBLIC', 'rpName': "Not for Public Consumption"})
            SubElement(context, '{http://cosimo.stanford.edu/sdr/metsrights/}Permissions',
                       {'DISCOVER': 'true', 'DISPLAY': 'true', 'MODIFY': 'false', 'DELETE': 'false'})
            context2 = SubElement(declaration, '{http://cosimo.stanford.edu/sdr/metsrights/}Context',
                                 {'CONTEXTCLASS': 'REPOSITORY MGR', 'rpName': "Admin Only"})
            SubElement(context2, '{http://cosimo.stanford.edu/sdr/metsrights/}Permissions',
                       {'DISCOVER': 'true', 'DISPLAY': 'true', 'MODIFY': 'false', 'DELETE': 'false'})
        elif data_file.get('file_embargoed_until', None):
            context1 = SubElement(declaration, '{http://cosimo.stanford.edu/sdr/metsrights/}Context',
                                  {'CONTEXTCLASS': 'GENERAL PUBLIC', 'end-date': data_file['file_embargoed_until'],
                                   'rpName': "Embargoed Bitstream"})
            SubElement(context1, '{http://cosimo.stanford.edu/sdr/metsrights/}Permissions',
                       {'DISCOVER': 'false', 'DISPLAY': 'false', 'MODIFY': 'false', 'DELETE': 'false'})
            context2 = SubElement(declaration, '{http://cosimo.stanford.edu/sdr/metsrights/}Context',
                                  {'CONTEXTCLASS': 'GENERAL PUBLIC', 'start-date': data_file['file_embargoed_until'],
                                   'rpName': "Public Bitstream"})
            SubElement(context2, '{http://cosimo.stanford.edu/sdr/metsrights/}Permissions',
                       {'DISCOVER': 'true', 'DISPLAY': 'true', 'MODIFY': 'false', 'DELETE': 'false'})
        else:
            today = datetime.now().strftime("%Y-%m-%d")
            context = SubElement(declaration, '{http://cosimo.stanford.edu/sdr/metsrights/}Context',
                                 {'CONTEXTCLASS': 'GENERAL PUBLIC', 'start-date': today, 'rpName': "Public Bitstream"})
            SubElement(context, '{http://cosimo.stanford.edu/sdr/metsrights/}Permissions',
                       {'DISCOVER': 'true', 'DISPLAY': 'true', 'MODIFY': 'false', 'DELETE': 'false'})

        return

    def file_source_metadata(self, data_file, count):
        sourcemd = SubElement(self.amdsec, 'sourceMD', {'ID': 'sourceMD_%d' % count})
        mdwrap = SubElement(sourcemd, 'mdWrap', {'MDTYPE': 'OTHER', 'OTHERMDTYPE': 'AIP-TECHMD'})
        xmldata = SubElement(mdwrap, 'xmlData')
        dim = SubElement(xmldata, '{http://www.dspace.org/xmlns/dspace/dim}dim', {'dspaceType': 'BITSTREAM'})
        title = SubElement(dim, '{http://www.dspace.org/xmlns/dspace/dim}field',
                            {'mdschema': 'dc', 'element': 'title'})
        title.text = data_file.get('file_name', '')
        if data_file.get('file_description', None):
            description = SubElement(dim, '{http://www.dspace.org/xmlns/dspace/dim}field',
                            {'mdschema': 'dc', 'element': 'description'})
            if isinstance(data_file['file_description'], list):
                description.text = data_file['file_description'][0]
            else:
                description.text = data_file['file_description']
        if data_file.get('file_mime_type', None):
            mime_type = SubElement(dim, '{http://www.dspace.org/xmlns/dspace/dim}field',
                                {'mdschema': 'dc', 'element': 'format', 'qualifier': 'mimetype'})
            mime_type.text = data_file.get('file_mime_type', '')
        if data_file.get('software', None):
            software = SubElement(dim, '{http://www.dspace.org/xmlns/dspace/dim}field',
                                {'mdschema': 'dc', 'element': 'format'})
            if isinstance(data_file['software'], list):
                software.text = data_file['software'][0]
            else:
                software.text = data_file['software']
        return

    def flatten_data(self):
        # embargoed_until_date
        # if self.data.get('embargo', None) == 'True' and self.data.get('publication_date', None):
        #     self.data['embargoed_until_date'] = self.data.get('publication_date')
        # Authors and supervisors
        author_list = self.data.get('authors', [])
        self.data['author_names'] = []
        self.data['author_orcids'] = []
        self.data['supervisor_names'] = []
        self.data['supervisor_orcids'] = []
        for author in author_list:
            author_name = ''
            if author.get('family_name', None) and author.get('given_names', None):
                author_name = "%s, %s" % (author['family_name'], author['given_names'])
            elif author.get('family_name', None):
                author_name = author['family_name']
            elif author.get('given_names', None):
                author_name = author['given_names']

            if author_name:
                self.data['author_names'].append(author_name)
            if author.get('orcid', None):
                self.data['author_orcids'].append(author_name + " [" + author['orcid'] + "]")

            if author.get('supervisor', None):
                if author_name:
                    self.data['supervisor_names'].append(author_name)

        # iscitedbydoi / iscitedbyurl
        if self.data.get('iscitedby', None):
            if self.data['iscitedby'].startswith("10.") or self.data['iscitedby'].startswith("doi:10."):
                self.data['iscitedbydoi'] = self.data['iscitedby']
            else:
                self.data['iscitedbyurl'] = self.data['iscitedby']
        # resources by type
        self.data['resources_webpage'] = []
        self.data['resources_sourcecode'] = []
        self.data['resources_otherpublication'] = []
        self.data['resources_conferenceoutput'] = []
        self.data['resources_otherdataset'] = []
        self.data['resources_report'] = []
        self.data['resources_blog'] = []
        self.data['resources_other'] = []
        for resource in self.data.get('resources', []):
            resource_url = resource.get('url', None)
            if not resource_url:
                continue
            if resource.get('type', None) == 'webpage':
                self.data['resources_webpage'].append(resource_url)
            elif resource.get('type', None) == 'sourcecode':
                self.data['resources_sourcecode'].append(resource_url)
            elif resource.get('type', None) == 'otherpublication':
                self.data['resources_otherpublication'].append(resource_url)
            elif resource.get('type', None) == 'conferenceoutput':
                self.data['resources_conferenceoutput'].append(resource_url)
            elif resource.get('type', None) == 'otherdataset':
                self.data['resources_otherdataset'].append(resource_url)
            elif resource.get('type', None) == 'report':
                self.data['resources_report'].append(resource_url)
            elif resource.get('type', None) == 'blog':
                self.data['resources_blog'].append(resource_url)
            elif resource.get('type', None) == 'other':
                self.data['resources_other'].append(resource_url)
        # funder_project_id
        # format is funders.name (funders.project_id)
        self.data['funder_project_id'] = []
        for funder in self.data.get('funders', []):
            if funder.get('name', None) and funder.get('project_id', None):
                self.data['funder_project_id'].append("%s (%s)"% (funder.get('name'), funder.get('project_id')))
            elif funder.get('name', None):
                self.data['funder_project_id'].append(funder.get('name'))
            elif funder.get('project_id', None):
                self.data['funder_project_id'].append("(%s)"% funder.get('project_id'))
        # submitter
        if self.data.get('given_names', None) and self.data.get('family_name', None):
            self.data['submitter'] = "%s, %s" % (self.data.get('family_name'), self.data.get('given_names'))
        elif self.data.get('family_name', None):
            self.data['submitter'] = self.data['family_name']
        elif self.data.get('given_names', None):
            self.data['submitter'] = self.data['given_names']
        # license
        self.data['license_text'] = ''
        self.data['license_uri'] = ''
        if self.data.get('license', None):
            self.data['license_text'] = self.data['license'].get('text', '')
            self.data['license_uri'] = self.data['license'].get('uri', '')
         # file format
        formats = []
        for f in self.data.get("files", []):
            for software in f.get("software", []):
                formats.append(software)
        self.data["format"] = formats
        return


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
