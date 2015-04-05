# openeye
News Aggregator

Suzanne,
John,
Carlo,
Ivo,
Tejaswini

How to run:
  1. Get a solr instance running by entering the following on the commandline (note solr will run until you shut it down):
    1. curl -O http://apache.mirror1.spango.com/lucene/solr/5.0.0/solr-5.0.0.tgz
    2. tar zxf solr-5.0.0.tgz
    3. rm solr-5.0.0.tgz
    4. cd solr-5.0.0
    5. bin/solr start -e cloud -noprompt
  3. Enter the following commands in the commandline to install the appropriate python libraries. 
    1. sudo pip install Flask
    2. easy_install solrpy
    3. pip install -U textblob
    4. python -m textblob.download_corpora
  5. Checkout our project from github
    1. git clone https://github.com/johnespinosa/openeye
    2. cd openeye
  6. run the website by entering the following command from the root directory of the project
    1. python openeye_server.py
  7. Enter the url specified in the output from running openeye_server.py into your favorite web browser and use OpenEye!
  8. Bob's your uncle.

How to shut down:
  1. Stop the openeye server:
    1. control + C in the terminal you entered "python openeye_server.py"
  2. Stop the solr instance:
    1. Navigate into the solr-5.0.0 directory you started solr in
    2. bin/solr stop -all
