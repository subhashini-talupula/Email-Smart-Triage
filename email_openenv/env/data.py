from .models import Email

EMAIL_DATA = {
    "easy": [
        Email(subject="Win a FREE iPhone!!!", body="Click now", sender="spam@fake.com"),
        Email(subject="Meeting tomorrow", body="Team sync at 10 AM", sender="boss@company.com"),
        Email(subject="Python Essentials 2 invitation", body="Please accept invitation in My Learning", sender="faculty@vignan.edu"),
    ],
    "medium": [
        Email(subject="Project deadline extended", body="Submit by Friday", sender="manager@company.com"),
        Email(subject="Dinner tonight?", body="Let's meet at 8", sender="friend@gmail.com"),
        Email(subject="Invoice #2041 pending", body="Payment due by Friday", sender="billing@vendor.com"),
    ],
    "hard": [
        Email(subject="URGENT: Account issue", body="Check immediately", sender="support@bank.com"),
        Email(subject="Special offer just for you", body="Limited deal", sender="promo@shop.com"),
        Email(subject="Security alert: verify login", body="New login detected. Verify now with OTP", sender="alerts@secureapp.com"),
        Email(subject="Summer sale - 40% discount", body="Use coupon SAVE40 at checkout", sender="newsletter@store.com"),
    ]
}