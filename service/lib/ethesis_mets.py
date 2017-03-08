from xml.etree.ElementTree import Element, SubElement, Comment, tostring, register_namespace
from xml.dom import minidom
from datetime import datetime
import os, codecs


class EthesisMets:
    def __init__(self, thesis):
        self.terms = {
            'title': {'mdschema': 'dc', 'element': 'title'},
            'type': {'mdschema': 'dc', 'element': 'type'},
            'author_names': {'mdschema': 'dc', 'element': 'contributor', 'qualifier': 'author'},
            'staff_ids': {'mdschema': 'pubs', 'element': 'staff-id'},
            'emails': {'mdschema': 'cam', 'element': 'externalEmail'},
            'author_orcids': {'mdschema': 'dc', 'element': 'contributor', 'qualifier': 'orcid'},
            'supervisor_names': {'mdschema': 'cam', 'element': 'supervisor'},
            'supervisor_orcids': {'mdschema': 'cam', 'element': 'supervisor', 'qualifier': 'orcid'},
            'awarding_institution': {'mdschema': 'dc', 'element': 'publisher', 'qualifier': 'institution'},
            'college': {'mdschema': 'dc', 'element': 'publisher', 'qualifier': 'college'},
            'faculty': {'mdschema': 'dc', 'element': 'publisher', 'qualifier': 'department'},
            'qualification_level': {'mdschema': 'dc', 'element': 'type', 'qualifier': 'qualificationlevel'},
            'degree': {'mdschema': 'dc', 'element': 'type', 'qualifier': 'qualificationname'},
            'degree_title': {'mdschema': 'dc', 'element': 'type', 'qualifier': 'qualificationtitle'},
            'date_awarded': {'mdschema': 'dc', 'element': 'date', 'qualifier': 'issued'},
            'abstract': {'mdschema': 'dc', 'element': 'description', 'qualifier': 'abstract'},
            'keywords': {'mdschema': 'dc', 'element': 'subject'},
            'funding': {'mdschema': 'dc', 'element': 'description', 'qualifier': 'sponsorship'},
            'language': {'mdschema': 'dc', 'element': 'language', 'qualifier': 'iso'},
            'third_party_copyright_notes': {'mdschema': 'dc', 'element': 'rights', 'qualifier': 'general'},
            'license_text': {'mdschema': 'dc', 'element': 'rights'},
            'license_uri': {'mdschema': 'dc', 'element': 'rights', 'qualifier': 'uri'},
            'comments': {'mdschema': 'dc', 'element': 'description'},
            'access_type': {'mdschema': 'cam', 'element': 'restriction'},
            "format" : {"mdschema" : "dc", "element" : "format"}
        }
        # Form metadata not used
        # access_reason
        # open_access_ip_confirmed
        # open_access_confidentiality_confirmed
        # authenticity_agreement
        # distribution_license

        # Metadata not collected
        """
            <dim:field mdschema="rioxxterms" element="licenseref" qualifier="startdate">
                Licence start date | embargo lift date
            </dim:field>
        """

        # FIXME: shared secret.
        self.admin_files = [thesis["id"] + '_confirmations.txt']

        register_namespace('xlink', 'http://www.w3.org/1999/xlink')
        register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        register_namespace('dim', 'http://www.dspace.org/xmlns/dspace/dim')
        register_namespace('', 'http://www.loc.gov/METS/')
        register_namespace('premis', 'http://www.loc.gov/standards/premis')
        register_namespace('rights', 'http://cosimo.stanford.edu/sdr/metsrights/')
        self.thesis = thesis
        self.id = self.thesis['id']
        self.flatten_data()
        self.mets = Element('{http://www.loc.gov/METS/}mets', {
            'ID': "theses_mets",
            'OBJID': self.id,
            'TYPE': 'DSPace ITEM',
            'PROFILE': 'DSpace METS SIP Profile 1.0',
            '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation':
                'http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd'
        })
        self.amdsec = None
        return

    def save_xml(self):
        file_path = os.path.join(self.thesis['dir'], 'mets.xml')
        if not os.path.exists(self.thesis['dir']):
            os.makedirs(self.thesis['dir'])
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
        if not self.thesis.get('type', None):
            self.thesis['type'] = ['Thesis']
        for term, attributes in self.terms.iteritems():
            if not self.thesis.get(term, None):
                continue
            vals = self.thesis[term]
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
        for thesis_file in self.thesis['files']:
            if thesis_file['file_name'] in self.admin_files:
                continue
            self.amdsec = SubElement(self.mets, 'amdSec', {'ID': 'amdSec_%d' % count})
            self.file_tech_metadata(thesis_file, count)
            self.file_rights_metadata(thesis_file, count)
            self.file_source_metadata(thesis_file, count)
            count += 1

        # admin files
        for thesis_file in self.thesis['files']:
            if not thesis_file['file_name'] in self.admin_files:
                continue
            self.amdsec = SubElement(self.mets, 'amdSec', {'ID': 'amdSec_%d' % count})
            self.file_tech_metadata(thesis_file, count)
            self.file_rights_metadata(thesis_file, count, type='admin')
            self.file_source_metadata(thesis_file, count)
            count += 1
        return

    def file_section_metadata(self):
        count = 1
        filesec = SubElement(self.mets, 'fileSec')
        # content files
        filegrp1 = SubElement(filesec, 'fileGrp', {'ID': 'fileGrp_1', 'USE': 'CONTENT'})
        sequence = 1
        for thesis_file in self.thesis['files']:
            if thesis_file['file_name'] in self.admin_files:
                continue
            fileprop = SubElement(filegrp1, 'file', {
                'GROUPID': 'fileGrp_1',
                'ID': 'file_%d' % count,
                'MIMETYPE': thesis_file.get('file_mime_type', ''),
                'SEQ': '%d' % sequence,
                'ADMID': 'amdSec_%d' % count
            })
            SubElement(fileprop, 'FLocat', {'LOCTYPE': 'URL', '{http://www.w3.org/1999/xlink}href':
                                                                            thesis_file.get('file_name', '')})
            count += 1
            sequence += 1

        # admin files
        filegrp2 = SubElement(filesec, 'fileGrp', {'ID': 'fileGrp_2', 'USE': 'ADMIN'})
        # sequence = 1
        for thesis_file in self.thesis['files']:
            if not thesis_file['file_name'] in self.admin_files:
                continue
            fileprop = SubElement(filegrp2, 'file', {
                'GROUPID': 'fileGrp_2',
                'ID': 'file_%d' % count,
                'MIMETYPE': thesis_file.get('file_mime_type', ''),
                'SEQ': '%d' % sequence,
                'ADMID': 'amdSec_%d' % count
            })
            SubElement(fileprop, 'FLocat', {'LOCTYPE': 'URL', '{http://www.w3.org/1999/xlink}href':
                                                                            thesis_file.get('file_name', '')})
            count += 1
            sequence += 1
        return

    def struct_metadata(self):
        structmap = SubElement(self.mets, 'structMap', {'ID': 'structMap_1', 'LABEL': 'structure', 'TYPE': 'LOGICAL'})
        div = SubElement(structmap, 'div', {'ID': 'structMap_div_1', 'DMDID': 'dmdSec_1', 'TYPE': 'DSpace Object'})
        for count in range(1, len(self.thesis['files']) + 1):
            div2 = SubElement(div, 'div', {'ID': 'structMap_div_%d' % (count+1)})
            SubElement(div2, 'fptr', {'FILEID': 'file_%d' % count})
        return

    def file_tech_metadata(self, thesis_file, count):
        techmd = SubElement(self.amdsec, 'techMD', {'ID': 'techMD_%d' % count})
        mdwrap = SubElement(techmd, 'mdWrap', {'MDTYPE': 'PREMIS'})
        xmldata = SubElement(mdwrap, 'xmlData', {'{http://www.w3.org/2001/XMLSchema-instance}schemaLocation':
                                                 'http://www.loc.gov/standards/premis http://www.loc.gov/standards/premis/PREMIS-v1-0.xsd'})
        premis_premis = SubElement(xmldata, '{http://www.loc.gov/standards/premis}premis')
        premis_object = SubElement(premis_premis, '{http://www.loc.gov/standards/premis}object')
        premis_chr = SubElement(premis_object, '{http://www.loc.gov/standards/premis}objectCharacteristics')
        if thesis_file.get('file_fixity', None):
            premis_fixity = SubElement(premis_chr, '{http://www.loc.gov/standards/premis}fixity')
            premis_mda = SubElement(premis_fixity, '{http://www.loc.gov/standards/premis}messageDigestAlgorithm')
            premis_mda.text = thesis_file['file_fixity'].get('type', '')
            premis_digest = SubElement(premis_fixity, '{http://www.loc.gov/standards/premis}messageDigest')
            premis_digest.text = thesis_file['file_fixity'].get('value', '')
        if thesis_file.get('file_size', None):
            premis_size = SubElement(premis_chr, '{http://www.loc.gov/standards/premis}size')
            premis_size.text = unicode(thesis_file['file_size'])
        premis_format = SubElement(premis_chr, '{http://www.loc.gov/standards/premis}format')
        premis_fd = SubElement(premis_format, '{http://www.loc.gov/standards/premis}formatDesignation')
        premis_fn = SubElement(premis_fd, '{http://www.loc.gov/standards/premis}formatName')
        premis_fn.text = thesis_file.get('file_mime_type', '')
        premis_original_fn = SubElement(premis_object, '{http://www.loc.gov/standards/premis}originalName')
        premis_original_fn.text = thesis_file.get('file_name', '')
        return

    def file_rights_metadata(self, thesis_file, count, type=None):
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
        elif thesis_file.get('file_embargoed_until', None):
            context1 = SubElement(declaration, '{http://cosimo.stanford.edu/sdr/metsrights/}Context',
                                  {'CONTEXTCLASS': 'GENERAL PUBLIC', 'end-date': thesis_file['file_embargoed_until'],
                                   'rpName': "Embargoed Bitstream"})
            SubElement(context1, '{http://cosimo.stanford.edu/sdr/metsrights/}Permissions',
                       {'DISCOVER': 'false', 'DISPLAY': 'false', 'MODIFY': 'false', 'DELETE': 'false'})
            context2 = SubElement(declaration, '{http://cosimo.stanford.edu/sdr/metsrights/}Context',
                                  {'CONTEXTCLASS': 'GENERAL PUBLIC', 'start-date': thesis_file['file_embargoed_until'],
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

    def file_source_metadata(self, thesis_file, count):
        sourcemd = SubElement(self.amdsec, 'sourceMD', {'ID': 'sourceMD_%d' % count})
        mdwrap = SubElement(sourcemd, 'mdWrap', {'MDTYPE': 'OTHER', 'OTHERMDTYPE': 'AIP-TECHMD'})
        xmldata = SubElement(mdwrap, 'xmlData')
        dim = SubElement(xmldata, '{http://www.dspace.org/xmlns/dspace/dim}dim', {'dspaceType': 'BITSTREAM'})
        title = SubElement(dim, '{http://www.dspace.org/xmlns/dspace/dim}field',
                            {'mdschema': 'dc', 'element': 'title'})
        title.text = thesis_file.get('file_name', '')
        if thesis_file.get('file_description', None):
            description = SubElement(dim, '{http://www.dspace.org/xmlns/dspace/dim}field',
                            {'mdschema': 'dc', 'element': 'description'})
            if isinstance(thesis_file['file_description'], list):
                description.text = thesis_file['file_description'][0]
            else:
                description.text = thesis_file['file_description']
        if thesis_file.get('file_mime_type', None):
            mime_type = SubElement(dim, '{http://www.dspace.org/xmlns/dspace/dim}field',
                                {'mdschema': 'dc', 'element': 'format', 'qualifier': 'mimetype'})
            mime_type.text = thesis_file.get('file_mime_type', '')
        if thesis_file.get('software', None):
            software = SubElement(dim, '{http://www.dspace.org/xmlns/dspace/dim}field',
                                {'mdschema': 'dc', 'element': 'format'})
            if isinstance(thesis_file['software'], list):
                software.text = thesis_file['software'][0]
            else:
                software.text = thesis_file['software']
        return

    def flatten_data(self):
        # Authors
        author_list = self.thesis.get('authors', [])
        self.thesis['author_names'] = []
        self.thesis['staff_ids'] = []
        self.thesis['emails'] = []
        self.thesis['author_orcids'] = []
        for author in author_list:
            given_names = ''
            if author.get('given_names', None):
                given_names = author.get('given_names')
                if isinstance(given_names, list):
                    given_names = ' '.join(given_names)
            author_name = "%s, %s" % (author.get('family_name', ''), given_names)
            self.thesis['author_names'].append(author_name)
            if author.get('crsid', None):
                self.thesis['staff_ids'].append(author['crsid'])
            if author.get('email_id', None):
                self.thesis['emails'].append(author['email_id'])
            if author.get('orcid', None):
                self.thesis['author_orcids'].append(author_name + " [" + author['orcid'] + "]")
        # Supervisors
        supervisor_list = self.thesis.get('supervisors', [])
        self.thesis['supervisor_names'] = []
        self.thesis['supervisor_orcids'] = []
        for supervisor in supervisor_list:
            given_names = ''
            if supervisor.get('given_names', None):
                given_names = supervisor.get('given_names')
                if isinstance(given_names, list):
                    given_names = ' '.join(given_names)
            supervisor_name = "%s, %s" % (supervisor.get('family_name', ''), given_names)
            self.thesis['supervisor_names'].append(supervisor_name)
            if supervisor.get('orcid', None):
                self.thesis['supervisor_orcids'].append(supervisor_name + " [" + supervisor['orcid'] + "]")
        # license
        self.thesis['license_text'] = ''
        self.thesis['license_uri'] = ''
        if self.thesis.get('license', None):
            self.thesis['license_text'] = self.thesis['license'].get('text', '')
            self.thesis['license_uri'] = self.thesis['license'].get('uri', '')
        # access_type
        self.thesis['access_type'] = ''
        if self.thesis.get('access', None):
            self.thesis['access_type'] = self.thesis['access'].get('type', '')
        # file format
        formats = []
        for f in self.thesis.get("files", []):
            for software in f.get("software", []):
                formats.append(software)
        self.thesis["format"] = formats
        return


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
