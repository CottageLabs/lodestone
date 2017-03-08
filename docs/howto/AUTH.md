# How to Set up Authentication

As the forms interface is a JavaScript application which posts data via
an API to a separate back-end, the user login and authentication procedures
are slightly complex.

We have defined two approaches to authenticating a user in the desired
environment:

(See UserLoginPatterns.png)

The first option is to set the user up to authenticate using the native
authentication mechanism of the environment the forms will be deployed in.

If this is Drupal, then simply place the forms on a Drupal page which requires
the user to be authenticated for them to see.

The second option is to set the user up to authenticate using a Single-Sign On
mechanism.  In this case the authentication likely happens as the user
passes through the Apache web server, so the pages in the CMS (e.g. Drupal)
do not need to have the native authentication enabled.

In either case, in order for the forms to communicate securely with the 
back-end, the Apache which presents the web interface for the CMS must
also provide a Reverse Proxy for the server where the Lodestone back-end
is installed.  This way, SSO authentication remains in effect wherever
needed.

(See /drupal/apache-ssl.conf)

The Lodestone back-end then just needs to be configured at the lowest level
possible (i.e the firewall) to only accept traffic from the IP address
of the CMS.  This means that back-end does not need to be aware of the
user's SSO credentials.