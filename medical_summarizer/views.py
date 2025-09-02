from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render 
import smtplib
from medical_summarizer.credentials import email, passward
from cq.models import contactd, queryd

def about (request):
    return render(request, "about.html")


def contact(request):
    if request.method == "POST":
        Name = request.POST.get("Name")
        Email = request.POST.get("Email")
        Subject = request.POST.get("Subject")
        Message = request.POST.get("Message")

        # Debug: print all POST data
        print("POST data:", request.POST)

        # Build the email text
        msg = f"""
        Type : "Contact"
        Name: {Name}
        Email: {Email}
        Subject: {Subject}
        Message: {Message}
        """
        # Call your mail function
        if Message!= None:
            database = contactd(name = Name, email = Email, subject = Subject, message = Message)
            database.save()
            mailtocontact(msg)

        return render(request,"contactreached.html")

    else:
        return render(request, "contact.html")

def contactr (request):
    
    return render(request, "contactreached.html")


def query(request):
    if request.method == "POST":
        Name = request.POST.get("name")
        Query = request.POST.get("description")

        msg = f"""
        Type : "Query"
        Name: {Name}
        Description: {Query}
        """
        if Query:
            database = queryd(name = Name, message = Query)
            database.save()
            mailtocontact(msg)

        return render(request, "contactreached.html")

def mailtocontact(data):    
    obj = smtplib.SMTP('smtp.gmail.com', 587)
    obj.starttls()
    obj.login(email, passward)
    obj.sendmail(email, ["issuatstudy090@gmail.com","singhaditi9210@gmail.com"], data)
    obj.quit()