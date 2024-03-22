# UserTrustSystem

This is an application that could be used by staff members in the Content teams to track and record how trust worthy an indiviudal contributor is. 

## What is basic requirement

Employees need a way of documenting their evidenced understanding about the trustworthy-ness of differnt contributors. 

Owning employees for the system known as 'Admins' should be able to delete or edit individuals who have signed up to the web app in order to remove their permissions or upgrade them also to be admin users.

This system utilises a users table to contain the staff member and a userstatus table which is used to track this trustworthy metric. Also storing this data within the database means that other systems could be adapted to  access this data when evaluating user submitted information.

There are 4 options (Neutral, Trusted, Suspicious, Shadow-banned) as well as a reason which can be added to a user.

## How does it work

At a basic level a staff member can sign up to the system and view other staff members who have signed up, as well as viewing all User statuses that have been added by these staff members.  

# How to use this app

## Accessing hosted application

This application is deployed to Render following a CI/CD workflow within Github actions. To access the live production version of this code go to the following link. 

https://drew-assignment-deployment.onrender.com/

A standard account can be created via the registeration form, or the following can be used. 
- username: notanadmin
- password: iamnotanadmin

## Launching locally

I would reccomend using the hosted application as there are a few requirements to run this code locally. 
- You must install Python 3

You will then want to install the requirements.txt file using 

```
pip install -r requirements. txt
```

To run the code locally you will need to navigate to the root folder of the application and run the following to generate the database;

```
python3 app.py
```

You can then run the application with, note: this will launch using http protocols. So i'd reccomend using the Render link!

```
flask run
```