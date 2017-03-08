# DSpace Setup

This directory holds DSpace configuration files and documentation for the time being, as a convenient place to
look after them until we figure out where they really should go

## Files

### PDF Cover Page

Files:
* config/modules/curate.cfg - configuration to allow PDF Cover pages to be generated as a curation task
* config/modules/disseminate-citations.cfg - configuration of the PDF Cover page generator itself
* xmlui/themes/Mirage/lib/xsl/aspect/artifactbrowser/item-view.xsl - chnages to the UI to correctly display files with PDF cover pages

You need to update your DSpace configuration by either replacing the current configuration with the one supplied here, or merging the configs supplied here with your existing config

    cp config/modules/curate.cfg [dspace]/config/modules
    cp config/modules/disseminate-citations.cfg [dspace]/config/modules
    cp xmlui/themes/Mirage/lib/xsl/aspect/artifactbrowser/item-view.xsl [tomcat]/webapps/xmlui/themes/Mirage/lib/xsl/aspect/artifactbrowser/
    
Note that we need to think more carefully about how to put the item-view.xsl file into the repository build.

You need to restart tomcat after deploying these changes.

### Theses Metadata Schema

Files:
* config/registries/thesis-metadata.xml - the schema file that describes the required metadata

The metadata required to support the theses deposit interface schema

You need to import this into your DSpace with:

    ./dspace registry-loader -metadata [lodestone path]/dspace/config/registries/thesis-metadata.xml
    
Once you've done this, you need to restart tomcat (if it was running in the first place), otherwise you will get UI errors.

### Data Metadata Schema

Files:
* config/registries/data-metadata.xml - the schema file that describes the required metadata

The metadata required to support the data deposit interface schema

You need to import this into your DSpace with:

    ./dspace registry-loader -metadata [lodestone path]/dspace/config/registries/data-metadata.xml
    
Once you've done this, you need to restart tomcat (if it was running in the first place), otherwise you will get UI errors.

### SWORD Configuration

Files:
* config/modules/swordv2-server.cfg - configuration for swordv2 server setup to enable correct interaction with deposit forms

You need to update your DSpace configuration by merging the configs supplied here with your existing config.  The configuration values
that are affected are:

* statement.bundles - adds the DISPLAY bundle to the list of exposed bundles, which means files affected by the PDF cover page will still be visible via SWORD
* simpledc.xxxx - specifies the crosswalk from the DSpace metadata to the Sword Deposit Receipt
* atom.xxxx - specifies the crosswalk from the DSpace metadata to the Sword Deposit Receipt
* state.* - Lodestone assumes the DSpace defaults, so best to leave these exactly as they are

You need to restart tomcat after deploying these changes.

## Other Notes

### Collection Authorisation Settings

In order for the confirmations.txt and sword package.zip files to be secured from anonymous access you need to do the following:

* Go to the Authorisations for the collection we are depositing to (go via /xmlui/admin/authorize)
* Click on "DEFAULT_BITSTREAM_READ"
* Change the group from "Anonymous" to "Administrator"
* Hit save
