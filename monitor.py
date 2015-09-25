from collection_wrapper import CollectionWrapper
import metaactuators
from datetime import datetime, timedelta
import emailauth
from email.mime.text import MIMEText
import smtplib


def notify_email(content):
	server = smtplib.SMTP(emailauth.smtpURL)
	msg = MIMEText('"'+content+'"')
	msg['Subject']='Alert: Quiver is down'
	msg['From'] = emailauth.fromaddr
	msg
	msg['To'] = ",".join(emailauth.toaddrs)
	server.starttls()
	server.login(emailauth.username, emailauth.password)
	server.sendmail(emailauth.fromaddr, emailauth.toaddrs, msg.as_string())
	server.quit()

statColl = CollectionWrapper('status')
currCommands = statColl.load_dataframe({"under_contol":True})
notify_email(repr(currCommands))
