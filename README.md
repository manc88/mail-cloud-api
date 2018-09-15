## mail-cloud-api
[cloud.mail.ru]()  APIs over http

###### LIBS
requests lib needed
```
$pip install requests
```
###### Examples
```
import mailcloudapi
cloud = mailcloudapi.Cloud("youremail@mail.ru" , "yourpassword")
cloud.login()
```
###### load file to the cloud
```
cloud.add_file("/home/documents/file.txt" , "my_backup/myfiles/") 
```
###### create folder 
```
cloud.add_folder("/cat1/cat2")
```
###### remove anything 
```
cloud.remove("my_backup/myfiles/file.txt")
```
###### share the file
```
cloud.share("my_backup/myfiles/file.txt")
```
###### unshare the file
```
cloud.unshare("my_backup/myfiles/file.txt")
```
###### move anything anywhere
```
cloud.move("what/to/move.txt" "where/to/move/")
```
###### rename anything
```
cloud.rename("folder1/folder2", "folder1/newfolder2name")
```
###### to logout
```
cloud.logout()
```
