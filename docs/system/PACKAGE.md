# Lodestone Package Format

Lodestone uses a METS-based package format, natively understood
by DSpace.  A full worked example of the package can be found in the
directory

    docs/system/example_package
    
The package consists on a file called mets.xml, and any number of other
files in a flat file structure (i.e. no sub-directories).  One of the
other files may be a confirmations.txt file, which contains statements
indicating the declarations the user made through the deposit form.

## Metadata File: mets.xml

The metadata file - mets.xml - contains all the deposit package metadata, including
all the bibliographic information, file information, and access restrictions.  DSpace
understands this file format natively and will import all the metadata and files, and
apply the access restrictions.

### General form of the mets.xml file

The following stripped-down example shows the key parts of the mets.xml file, with
comments inline:

    <mets ID="theses_mets" OBJID="theses_uuid" TYPE="DSPace ITEM" PROFILE="DSpace METS SIP Profile 1.0"
          xmlns="http://www.loc.gov/METS/"
          xmlns:dim="http://www.dspace.org/xmlns/dspace/dim"
          xmlns:premis="http://www.loc.gov/standards/premis"
          xmlns:rights="http://cosimo.stanford.edu/sdr/metsrights/"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd">
    
        <metsHdr CREATEDATE="2016-07-27T00:00:00Z">
            <agent ROLE="CREATOR" TYPE="OTHER" OTHERTYPE="Lodestone">
                <name>Lodestone</name>
            </agent>
        </metsHdr>
        
        <!-- Descriptive metadata section, where all the bibliographic metadata goes -->
        <dmdSec ID="dmdSec_1">
            <mdWrap MDTYPE="OTHER" OTHERMDTYPE="DIM">
                <xmlData>
                    <dim:dim dspaceType="ITEM">
                        <dim:field mdschema="dc" element="contributor" qualifier="author">Family, Given</dim:field>
                        .... additional metadata fields ....
                    </dim:dim>
                </xmlData>
            </mdWrap>
        </dmdSec>
    
        <!-- Administrative metadata section, where technical, rights, and individual file metadata goes.
            You would have one section like this per file -->
        <amdSec ID="amdSec_1">
            <techMD ID="techMD_1">
                <mdWrap MDTYPE="PREMIS">
                    <xmlData xsi:schemaLocation="http://www.loc.gov/standards/premis http://www.loc.gov/standards/premis/PREMIS-v1-0.xsd">
                        
                        <!-- PREMIS technical metadata - containing the mimetype, the file size and the original file name -->
                        <premis:premis>
                            <premis:object>
                                <premis:objectCharacteristics>
                                    <premis:size>10201</premis:size>
                                    <premis:format>
                                        <premis:formatDesignation>
                                            <premis:formatName>application/pdf</premis:formatName>
                                        </premis:formatDesignation>
                                    </premis:format>
                                </premis:objectCharacteristics>
                                <premis:originalName>pdf1.pdf</premis:originalName>
                            </premis:object>
                        </premis:premis>
                    </xmlData>
                </mdWrap>
            </techMD>
            
            <rightsMD ID="rightsMD_1">
                <mdWrap MDTYPE="OTHER" OTHERMDTYPE="METSRIGHTS">
                    <xmlData xsi:schemaLocation="http://cosimo.stanford.edu/sdr/metsrights/ http://cosimo.stanford.edu/sdr/metsrights.xsd">
                    
                        <!-- METS rights XML for use in setting bitstream access policies -->
                        <rights:RightsDeclarationMD RIGHTSCATEGORY="LICENSED">
                            <rights:Context CONTEXTCLASS="GENERAL PUBLIC" end-date="2017-01-01" rpName="Embargoed Bitstream">
                                <rights:Permissions DISCOVER="false" DISPLAY="false" MODIFY="false" DELETE="false"/>
                            </rights:Context>
                            ... other access rights statements ...
                        </rights:RightsDeclarationMD>
                    </xmlData>
                </mdWrap>
            </rightsMD>
            
            <sourceMD ID="sourceMD_1">
                <mdWrap MDTYPE="OTHER" OTHERMDTYPE="AIP-TECHMD">
                    <xmlData>
                        <!-- DSpace native metadata to be attached to the bitstream -->
                        <dim:dim dspaceType="BITSTREAM">
                            <dim:field mdschema="dc" element="title">pdf1.pdf</dim:field>
                            ... additional file metadata ...
                        </dim:dim>
                    </xmlData>
                </mdWrap>
            </sourceMD>
        </amdSec>
    
        <!-- List of files associated with this item -->
        <fileSec>
            <fileGrp ID="fileGrp_1" USE="CONTENT">
                <file GROUPID="fileGrp_1" ID="file_1" MIMETYPE="application/pdf" SEQ="1" ADMID="amdSec_1">
                    <FLocat LOCTYPE="URL" xlink:href="pdf1.pdf"/>
                </file>
            </fileGrp>
        </fileSec>
        
        <!-- Structural information associating files with this item -->
        <structMap ID="structMap_1" LABEL="structure" TYPE="LOGICAL">
            <div ID="structMap_div_1" DMDID="dmdSec_1" TYPE="DSpace Object">
                <div ID="structMap_div_2">
                    <fptr FILEID="file_1"/>
                </div>
            </div>
        </structMap>
    </mets>


### Descriptive metadata

Descriptive metadata is provided using the DSpace Interchange Metadata (DIM) format.  This is a simple
format which mimics how DSpace represents metadata internally:

    <dim:field mdschema="schema_name" element="element_name" qualifier="qualifier_name">Metadata Value</dim:field>
    
For example:

    <dim:field mdschema="dc" element="contributor" qualifier="author">Family, Given</dim:field>
    
### Rights Metadata

DSpace rights for individual bitstreams are set by providing a suitable rights Context and Permissions 
using the METS rights XML:


    <rights:Context CONTEXTCLASS="Who it affects" end-date="when it expires" rpName="Arbitrary name for the policy">
        <rights:Permissions DISCOVER="true|false" DISPLAY="true|false" MODIFY="true|false" DELETE="true|false"/>
    </rights:Context>
    
For example, this specifies rights for the GENERAL PUBLIC (i.e. the Anonymous Group) which expire on 1st January 2017.  The
permissions given to the group are: no discovery, no display, no modify, no delete.  That is - embargo this item from 
the general public.

    <rights:Context CONTEXTCLASS="GENERAL PUBLIC" end-date="2017-01-01" rpName="Embargoed Bitstream">
        <rights:Permissions DISCOVER="false" DISPLAY="false" MODIFY="false" DELETE="false"/>
    </rights:Context>
    
You may wish to specify multiple rights per bitstream.  For example, alongside the embargo, you may want to
specify the rights for the administrator group:

    <rights:Context CONTEXTCLASS="REPOSITORY MGR" rpName="Admin Only">
        <rights:Permissions DISCOVER="true" DISPLAY="true" MODIFY="false" DELETE="false"/>
    </rights:Context>
    
### File Metadata

Files in DSpace can take a small subset of the total metadata registry, specified with DIM.  Only:

* Title (dc.title)
* Description (dc.description)
* Format (dc.format)

For example:

    <dim:field mdschema="dc" element="title">pdf1.pdf</dim:field>
    <dim:field mdschema="dc" element="description">This is a description of the file</dim:field>
    <dim:field mdschema="dc" element="format" qualifier="mimetype">application/pdf</dim:field>
    <dim:field mdschema="dc" element="format">Software name</dim:field>