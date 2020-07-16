# Instructions on how to obtain Google OAuth key:

1. Go to https://console.developers.google.com/
2. On the left hand side of the top bar, click on the selected project (if any) and then select "New Project" on the following pop up. 

![image](https://user-images.githubusercontent.com/36301625/87026746-da749880-c1e4-11ea-8b29-fae65e6dd051.png)

3. Fill in a name and optionally an organization 
4. After the project is created, make sure it is selected in the top left bar as shown in the previous image
5. Click on the "OAuth consent screen" from the sidebar, select "External" option an click on the "Create" button
6. On the following form, fill in just the "application name" and the "support email" fields and click "Save".
7. Then click on the "Credentials" tab, and then on "Create Credentials", and "OAuth Client ID" on the top
8. Select "Web Application", pick a name and add `http://localhost:8000` as "Authorized JavaScript Origins" and `http://localhost:8000/accounts/google/login/callback/` as "Authorised redirect URIs" and click "Create"