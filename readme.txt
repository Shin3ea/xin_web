Username: ammar
Password: 123456
Domain:   http://ml17x44z.pythonanywhere.com/

Agency  74
Name:                               Xin Zhang News Agency
URL:                                http://ml17x44z.pythonanywhere.com/
Unique Code:                        XIN

I used OneToOneFiled to extand built-in User model, so if you'd like to add author in the Author model you should createsuperuser in command line and it will automatically generate a author in the model, and then you should update the Name line in admin site for the corresponding author otherwise the 'Author Name' of the post that you post would be empty, because I aussume that every author has his name.

And I used auto_now_add to update the Post_Date for every instance of the Story model, thus you cannot modify the date on admin site.
