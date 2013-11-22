date >>/home/rapoadmin/public_html/rapoproject/rapoapp/MemberCount.txt
mysql -uroot rapodb -prootMY1! -e "select count(*) from socialaccount_socialaccount" | grep -v "count" >> /home/rapoadmin/public_html/rapoproject/rapoapp/MemberCount.txt
