# Drupal setup

There are the essential steps that need to be accomplished to ensure the web pages for thesis and data are available in Drupal

0. Install and activate the Nodeaccess module through the Drupal UI.

Once you have done this, you should have access to a "Grant" tab on the node edit page, which will allow you
to set fine-grained access controls to a page.

1. Update Jquery version for the application nodes <br>
   The application is built to work with version 1.12.4 of Jquery while Drupal natively currently runs a much older version of Drupal. <br>
   This is done by overwriting jquery data using the js_alterhook in a custom template

 * Create a new template by copying the existing template and placing it in sites/all/themes. <br>
   I have called the new template cl so it will be in sites/all/themes/cl

 * Add the following function (or add these lines to the existing function) cl_js_alter
 ```
 // Replace JS in page node/4
function cl_js_alter(&$javascript) {
  $nodes = array("node/1", "node/2", "node/3", "node/4", "node/5", "node/6", "node/7", "node/8", "node/9", "node/10", "node/11", "node/12")
  if (in_array(current_path(), $nodes)) {
    // Swap out jQuery to use an updated version of the library.
    $javascript['misc/jquery.js']['data'] = 'misc/cl/js/jquery.js';
  }
}
```
   The application needs 12 nodes and the above code assumes the node ids are 1 to 12. Change them according to the actual node ids of the pages created in Drupal
      * 3 for thesis with SSO login (list page, deposit form and view page for each record)
      * 3 for thesis with native Drupal login
      * 3 for data with SSO login
      * 3 for data with native drupal login

2. Copy the files in drupal/misc/cl to the misc directory in your Drupal installation

The files in drupal/misc/cl are symlinks, and you may wish to solidify them during copy:

```
cd drupal/misc/cl/
sudo cp -rL * /var/www/drupal.xxxxxxx.ac.uk/misc/cl/
cd /var/www/drupal.xxxxxxx..ac.uk/misc/cl/
sudo chown -R www-data:www-data *
```

3. Create the 12 nodes in Drupal
  * We created the content using the __basic page__ node type in Drupal
  * You need to set the content type (or text format) to php code for these nodes
  * The pages managed by native Drupal login needs to be visible only to authenticated users. We accomplished this using the node access module for Drupal to grant access on a per node basis.
  * The pages managed by SSO should be set to be accessible by anonymous users as Drupal does not manage the login in the case of SSO
  * the URL for each of the nodes needs to be set to an appropriate alias.
  * The code in the nodes also assumes that the python server api is available at /deposit/api for the SSO pages and at /external/api for the drupal pages
  * The content for each of the nodes is as in /drupal/*_node.html in the git repository

| *Node* | *Authentication method* | *Alisa URL* | *Nodeaccess settings* | *File with corresponding contents* |
| ---- | ---- | ---- | ---- | ---- |
| Thesis List | Drupal | /external/theses | administrator: view, edit, delete <br> authenticated user: view <br> external user: view | /drupal/thesis_list_node.html |
| Thesis Deposit | Drupal | /external/theses/form | administrator: view, edit, delete <br> authenticated user: view <br> external user: view | /drupal/thesis_deposit_node.html |
| Thesis Show | Drupal | /external/theses/show | administrator: view, edit, delete <br> authenticated user: view <br> external user: view | /drupal/thesis_show_node.html |
| Data List | Drupal | /external/data | administrator: view, edit, delete <br> authenticated user: view <br> external user: view | /drupal/data_list_node.html |
| Data Deposit | Drupal | /external/data/form | administrator: view, edit, delete <br> authenticated user: view <br> external user: view | /drupal/data_deposit_node.html |
| Data Show | Drupal | /external/data/show | administrator: view, edit, delete <br> authenticated user: view <br> external user: view | /drupal/data_show_node.html |
| Thesis List | SSO | /deposit/theses | administrator: view, edit, delete <br> authenticated user: view <br> anonymous user: view | /drupal/thesis_list_node.html |
| Thesis Deposit | SSO | /deposit/theses/form | administrator: view, edit, delete <br> authenticated user: view <br> anonymous user: view | /drupal/thesis_deposit_node.html |
| Thesis Show | SSO | /deposit/theses/show | administrator: view, edit, delete <br> authenticated user: view <br> anonymous user: view | /drupal/thesis_show_node.html |
| Data List | SSO | /deposit/data | administrator: view, edit, delete <br> authenticated user: view <br> anonymous user: view | /drupal/data_list_node.html |
| Data Deposit | SSO | /deposit/data/form | administrator: view, edit, delete <br> authenticated user: view <br> anonymous user: view | /drupal/data_deposit_node.html |
| Data Show | SSO | /deposit/data/show | administrator: view, edit, delete <br> authenticated user: view <br> anonymous user: view | /drupal/data_show_node.html |
| ---- | ---- | ---- | ---- | ---- |

As the data-* attribute paths are different for SSO and Native Drupal pages, be sure to check that they point to the correct URLs
when deploying the pages.

4. Set SSO authentication and a local path to the backend api in Apache

For example, include this in the appropriate sites-availabe file on the Drupal Apache:

    ProxyPass /deposit/api http://lodestone.xxxxxxx.ac.uk
    ProxyPassReverse /deposit/api http://lodestone.xxxxxxx.ac.uk
    
    ProxyPass /external/api http://lodestone.xxxxxx.ac.uk
    ProxyPassReverse /external/api http://lodestone.xxxxxxx.ac.uk

