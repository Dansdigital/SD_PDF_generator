# SD_PDF_generator

This python project converts a csv file to a array of dictionary objects. Each object has product data that is used to generate a PDF file.
The PDF file is created using PyFPDF library. Once the file is create it is uploaded to the wordpress website using Playwright. After the upload
it then deletes the file form the local directory. 

The login and save cookies file is used to save a state of login. So one skip the login in step to run the program consecutively. 
