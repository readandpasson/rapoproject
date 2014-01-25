date >>/home/rapoadmin/public_html/devrapo/rapoapp/MemberCount.txt
mysql -uroot test_db -pSQroot1! -e "select count(*) from socialaccount_socialaccount" | grep -v "count" >> /home/rapoadmin/public_html/devrapo/rapoapp/MemberCount.txt
