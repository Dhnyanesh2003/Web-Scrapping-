import tkinter as tk
from tkinter import filedialog, messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class EmailSender:
    def __init__(self, master):
        self.master = master
        self.master.title("Email Sender")
        self.master.geometry("1000x1000")

        # Labels and inputs for sender email and password
        self.label_sender_email = tk.Label(master, text="Enter your email address:")
        self.label_sender_email.pack(pady=10)

        self.sender_email_entry = tk.Entry(master, width=40)
        self.sender_email_entry.pack(pady=10)

        self.label_sender_password = tk.Label(master, text="Enter your email password (App Password for Gmail):")
        self.label_sender_password.pack(pady=10)

        self.sender_password_entry = tk.Entry(master, width=40, show="*")
        self.sender_password_entry.pack(pady=10)

        # Labels and input for receiver emails
        self.label_receiver_email = tk.Label(master, text="Enter recipient email addresses (comma separated):")
        self.label_receiver_email.pack(pady=10)

        self.receiver_email_entry = tk.Entry(master, width=40)
        self.receiver_email_entry.pack(pady=10)

        # Labels and input for subject
        self.label_subject = tk.Label(master, text="Enter the subject of the email:")
        self.label_subject.pack(pady=10)

        self.subject_entry = tk.Entry(master, width=40)
        self.subject_entry.pack(pady=10)

        # Labels and input for the message
        self.message_label = tk.Label(master, text="Enter your message:")
        self.message_label.pack(pady=10)

        self.message_entry = tk.Text(master, width=40, height=10)
        self.message_entry.pack(pady=10)

        # Attach file button
        self.attach_button = tk.Button(master, text="Attach File (PDF/Image)", command=self.attach_file)
        self.attach_button.pack(pady=10)

        # Send email button
        self.send_button = tk.Button(master, text="Send Email", command=self.send_email)
        self.send_button.pack(pady=10)

        # File path for attachment
        self.attachment_path = None

    def attach_file(self):
        """Allow the user to select a file for attachment."""
        self.attachment_path = filedialog.askopenfilename(title="Select a File", filetypes=[("PDF files", "*.pdf"), (
        "Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if self.attachment_path:
            messagebox.showinfo("File Selected", f"File selected: {self.attachment_path.split('/')[-1]}")

    def send_email(self):
        """Send the email with an optional attachment."""
        sender_email = self.sender_email_entry.get().strip()
        sender_password = self.sender_password_entry.get().strip()
        to_addresses = self.receiver_email_entry.get().strip()
        subject = self.subject_entry.get().strip()
        message = self.message_entry.get("1.0", "end-1c").strip()

        if not sender_email or not sender_password or not to_addresses or not subject or not message:
            messagebox.showerror("Error",
                                 "Please provide sender email, password, recipient email, subject, and message.")
            return

        to_addresses = to_addresses.split(",")  # Split multiple email addresses

        # SMTP server and login details
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        try:
            # Connect to the SMTP server
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)

                for recipient in to_addresses:
                    # Create a MIME message for each recipient
                    msg = MIMEMultipart()
                    msg["From"] = sender_email
                    msg["To"] = recipient.strip()  # Send to one recipient at a time
                    msg["Subject"] = subject

                    # Attach the message body
                    msg.attach(MIMEText(message, "plain"))

                    # Attach file if selected
                    if self.attachment_path:
                        with open(self.attachment_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition",
                                            f"attachment; filename={self.attachment_path.split('/')[-1]}")
                            msg.attach(part)

                    # Send the email to the current recipient
                    server.sendmail(sender_email, recipient.strip(), msg.as_string())

            messagebox.showinfo("Success", "Emails sent successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


# Initialize the Tkinter window
root = tk.Tk()
email_sender = EmailSender(root)
root.mainloop()
