The goal of the project is to have a application that is used as a regular text file that anyone can use without needing an additional application. It will run in the users browser, storing the information in local directory on the users computer.

## The process look like this

1. The first user creates a text document in their browser from the HTML app.
2. They can press commit changes, and export the file as a zip file.
3. The next user will then open the link provided (which is the HTML app) and import the zip file from the first user.
4. They can now edit the document, view the history of the document, and when they are done commit their changes and save them as a zip again, passing it onto the next user.

This creates an accesible paper trail that a user can see and anylize without being proficient with computers or git.

## Ideally the process will look like this: (A link which locally runs an HTML app, instead of sending an HTML app to the next user)

1. Opening the a link would run a HTML file locally on your device
2. create your text document.
3. Press commit change + export
4. Send the zip file to the next user
5. User 2 will open the link, and view the HTML app
6. Press import repository zip and choose the zip file sent by the previous user
7. They can now edit the document save, and export the changes
8. User 2 can now pass on the zip file which has the changes from themselves and the previous users.

## Practicle info for Hackathon

There are two versions on the git repository.

### One version

One version is made in python as a mockup, since we understand how to code in python and create a prototype we understand. This version will likely not work as it depends on python libraries that were installed on the computer which coded it.

### The second

The second is a fully AI coded version which works almost as desired, using an HTML app and zip files to transfer different versions of the text document. A current bug we have discovered is that after opening a zip file it is stored in the browsers cookies and you cannot create a new document without a history as the old history is still stored in the browser.
