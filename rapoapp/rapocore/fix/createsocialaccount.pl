$i=3;
while (<>){
chomp;
($first_name,$last_name ,$username,$uid)= split /,/,$_;
print " {\"pk\":", $i-1,", \"model\": \"socialaccount.socialaccount\", \"fields\": {\"uid\": \"",$uid,"\", \"last_login\": \"\", \"user\": ",$i,", \"provider\": \"facebook\", \"extra_data\": \"{\\\"username\\\": \\\"",$username,"\\\", \\\"website\\\": \\\"\\\"first_name\\\": \\\"",$first_name,"\\\", \\\"last_name\\\": \\\"",$last_name,"\\\", \\\"name\\\": \\\"",$first_name," ",$last_name,"\\\", \\\"email\\\": \\\"\\\"}\", \"date_joined\": \"2013-07-13T11:37:43\"}} \n";

$i++;
}

