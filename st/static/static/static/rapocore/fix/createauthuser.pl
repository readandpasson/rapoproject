$i=3;
while (<>){
chomp;
($first_name,$last_name ,$username)= split /,/,$_;
print "{\"pk\":",$i,",\"model\":\"auth.user\",\"fields\": {\"username\": \"", $username, "\", \"first_name\": \"", $first_name, "\", \"last_name\": \"", $last_name, "\",\"is_active\": true, \"is_superuser\": false, \"is_staff\": false, \"last_login\": \"2013-07-13T21:09:34\", \"groups\": [], \"user_permissions\": [], \"password\": \"!\", \"email\": \"\", \"date_joined\": \"2013-07-13T11:37:43\"}}, ";
print "\n";

$i++;
}
