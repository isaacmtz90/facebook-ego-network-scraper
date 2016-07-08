# facebook-ego-network-scraper
Scrape Facebook ego network using Python and SelenumHQ 


Get your Facebook friend network
Usage: python extract_ego.py <username> <password> <numerical_fb_id> <output file>
** username can also be the account email.

The output format is a .dot file (specify in the arguments)

This script uses a browser automation library and the Firefox browser.
Automates the actions using selenium

Install dependencies via Pip:
pip install splinter 
pip install selenium
pip install codecs
pip install requests

You will need your own FB numerical id, get it using http://theseotools.net/bulk-fb-id-finder or a similar tool.
Make sure to have a stable internet connection, may take some hours depending on the number if friends.

