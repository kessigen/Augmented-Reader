# TUTORIAL:

1. Follow setup instructions in [README.md](../README.md) on github:

   a. Once web app is loaded for the first time, go to http://localhost:3000. You will have access to the homepage. There will be some placeholders that are replaced as you upload more ebooks.

   ![Homepage](images/tutorial-homepage.jpg)

   b. Should you encounter the error below, directly set your OPENAI_API_KEY in the .env file and skip copy from env.example from the setup. After that, it should work

   ![OPENAI_API_KEY error](images/tutorial-missing-api-key-error.jpg)

2. a. Click on the 'upload book' icon at the bottom right of the screen to upload an epub file.

   ![Upload book icon](images/tutorial-upload-button.png)

   b. For this tutorial, we will choose an ebook from public domain ebooks from the gutenberg website. A sample epub has been provided in the [samples](../samples/) folder. If you wish, you can instead choose any ebook. However, this app has been built and works best with the older epub file versions. The file format is available on project gutenberg as shown below (in red):

   ![Project Gutenberg download options](images/tutorial-gutenberg-epub.jpg)

3. Loading will take some time (5 min) for the first book since backend is building the vector stores and DB for the first time. Once it is processed,You will receive a notification in the front end. You can then refresh the webpage and the new ebook sample.epub will be visible under the library section.

   ![Upload notification](images/tutorial-upload-success.jpg)

   ![Library](images/tutorial-library.jpg)

4. Click on it. You now have access to the reader interface and all its features.

   ![Reader interface](images/tutorial-reader.jpg)

## IN DEPTH VIEW OF DATA MODELS:

Should you be interested in visualizing the internal data structures and relationships that we obtain after processing the ebook, you can use django admin to view the tables created.

1. Creating a django superuser :

   a. If project is running, go to terminal where the backend is running and do Ctrl+ C. This stops the execution.

   b. Create a new django admin superuser by entering the command:
   `python manage.py createsuperuser`

   c. You will be prompted to enter your name, email and password. Just use fake details.

   ![createsuperuser](images/tutorial-createsuperuser.jpg)

   d. Once user is created successfully, restart the server using the command:
   `python manage.py runserver`.

   e. Go to the admin view in your browser http://127.0.0.1:8000/admin and login with user you created earlier

   f. You now have access to the app tables:

   ![Django admin](images/tutorial-admin-home.jpg)

   g. You now have access to all the book, chapters and event objects in the DB. For example :

   ![Book object](images/tutorial-admin-book.jpg)

The full view for one instance of sample.epub is shown below:

![All objects for sample.epub, part 1](images/tutorial-admin-objects-1.jpg)

![All objects for sample.epub, part 2](images/tutorial-admin-objects-2.jpg)
