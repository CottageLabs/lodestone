# SWORD Protocol Operations

This document outlines the SWORDv2 protocol operations that are used by Lodestone:

## Creating a new item in DSpace

Once a user has uploaded their files and saved their record, the following
exchange takes place, with the payload as the package described in PACKAGE.md

(See SWORDDeposit.png)

The package is POSTed to the DSpace, which ingests the contents to the 
collection, sets the access policies, and triggers the workflow.  It then
sends a Deposit Receipt back, and we record the Edit IRI for use later (this
is the main identifier used to track items with SWORDv2).

## Polling for updates on an item in DSpace

After an item has been successfully deposited, Lodestone polls
DSpace for regular updates on the status of the item, which is reported
to the end-user, and used to determine when post-deposit cleanup can take place
within Lodestone.

(See SWORDPoll.png)

First we GET the Edit-IRI which we stored from the original deposit.  This
gives back a copy of the Deposit Receipt.  Inside the Deposit Receipt we find
two kinds of identifier: an Atom Statement IRI and an ORE Statement IRI.  We first
attempt to retrieve the Atom Statement, and if that's not available we attempt
to retrieve the ORE Statement.  In DSpace we would expect both to be present,
and only one is required.  In the Statement we find information on the
current workflow state of an item, and we add that information to the Deposit
Tool's record for the item.  If the item has been archived, the deposit
tool then deletes its copies of the files uploaded by the user.
