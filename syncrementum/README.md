## Installation Instructions:

  1. **Install Apache**  
        - sudo apt-get update
        - sudo apt-get install apache2
  2. **Install mod_wsgi**
        - sudo apt-get install libapache2-mod-wsgi python-dev
        - if it is not automatically enabled run:
          - sudo a2enmod wsgi
  3. **Clone the repository into /var/www/**
        - git clone https://github.com/dmrs-inc/dmrs_reports.git
  4. **Change the database configuration in config.py**
  5. **Create the virtual environment and run requirements.txt**
        - create a system user called wsgi
        - su wsgi
        - virtualenv venv
        - source venv/bin/activate
        - pip install -r requirements.txt
        - if you hit a mysql error, run:
          -sudo apt-get install libmysqlclient-dev
  5. **Run the server locally to check for errors.**
        - python manage.py runserver
  6. **Give reading and editing permissions to  /var/www/dmrs_reports**
        - this will allow logging to work properly.
        - for more security, only give editing permissions to activity.log and error.log
  7. **Create a vhosts file**
        - sudo nano /etc/apache2/sites-available/dmrs_reports.conf
        ```html
            <VirtualHost \*:80>
              ServerName CHANGE_ME
              ServerAdmin rhallman@dmrs.net
              WSGIScriptAlias / /var/www/dmrs_reports/flasapp.wsgi
              <Directory /var/www/dmrs_reports/app/>
                Order allow,deny
                Allow from all
              </Directory>
              Alias /static /var/www/dmrs_reports/app/static/
              <Directory /var/www/dmrs_reports/app/static/>
                Order allow,deny
                Allow from all
              </Directory>
              ErrorLog ${APACHE_LOG_DIR}/error.log
              LogLevel warn
              CustomLog ${APACHE_LOG_DIR}/access.log combined
            </VirtualHost>
        ```  
        - Port 80 will need to be open in the firewall at this point.
        - If you try to browse to the page and you get an apache page with
          an access denied error, you will likely need to edit the part of
          the vhosts file that says:
            Order allow,deny
            Allow from all
  8. **Enable the hosts file**
        - sudo a2ensite dmrs_reports
  9. **Restart apache2**
        - sudo service apache2 restart

## Notes:

  **The Following is a list of hard-coded values in this project:**
        - The variables *admin_permission*, *Manager_permission*, and *User_permission*
          are found in config.py and are referenced throughout the views to determine
          what level of permission is required to access each view function.
        - The variable *choices* in config.py represents the possible fields that
          can be selected or filtered when creating an ad hoc report. This
          variable is referenced in the ad_hoc view in both the *create* and *edit*
          functions in the form by the name of *Ad_hoc*
        - The variable *Facility_codes* in config.py represents the facilities that
          are hospitals and is referenced in the function *hos_breakdown* in models.py.
        - The variables *LOG_ERROR* and *LOG_ACTIVITY* represent the paths where
          the activity and error logs are to be stored. These variables are referenced
          in logger_setup.py when the loggers are created.
        - The variable *shared* which is found in test_form.py represents the facilities
          that can be used in the shared service report. it is referenced in the form
          *SSreport*
        - The variable *hos_clin_choice* in test_form.py represents the choice
          between hospitals, clinics, and all facilities in in the form *Hospital*
        - The variable *group_choice* in test_form.py represents the ways in which
          the billing breakdown report can be grouped, and is referenced in the
          form by the name of *Billing* in test_form.py.
        - In management.py in the function *ssreport*, there are hard-coded values
          used to reference facility codes as well as the attn. line in the report.
