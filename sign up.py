import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from interface import SignLanguageApp  # Importing the interface class

# Excel file to store user data
FILE_NAME = "user_data.xlsx"

# Check if file exists, if not create it
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["First Name", "Last Name", "Email", "Password"])
    df.to_excel(FILE_NAME, index=False)

def open_interface():
    root.destroy()  # Close login window
    interface_root = tk.Tk()  # Create a new Tkinter window
    app = SignLanguageApp(interface_root)  # Start the sign language interface
    interface_root.mainloop()

def save_user():
    first_name = entry_first_name.get()
    last_name = entry_last_name.get()
    email = entry_email.get()
    password = entry_password.get()
    
    if not first_name or not last_name or not email or not password:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    df = pd.read_excel(FILE_NAME)
    if email in df["Email"].values:
        messagebox.showerror("Error", "Email already registered!")
        return
    
    new_user = pd.DataFrame({"First Name": [first_name], "Last Name": [last_name], "Email": [email], "Password": [password]})
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_excel(FILE_NAME, index=False)
    messagebox.showinfo("Success", "Sign Up successful!")
    switch_to_login()

def verify_login():
    email = login_email.get()
    password = login_password.get()
    
    df = pd.read_excel(FILE_NAME)
    if ((df["Email"] == email) & (df["Password"] == password)).any():
        messagebox.showinfo("Success", "Login successful!")
        open_interface()
    else:
        messagebox.showerror("Error", "Invalid credentials!")

def switch_to_signup():
    login_frame.pack_forget()
    signup_frame.pack()

def switch_to_login():
    signup_frame.pack_forget()
    login_frame.pack()

# Main Window
root = tk.Tk()
root.title("Sign Up / Login")
root.geometry("400x500")
root.configure(bg="#1E1E1E")

# Tabs Frame
tabs_frame = tk.Frame(root, bg="#333333")
tabs_frame.pack(fill="x")

btn_signup = tk.Button(tabs_frame, text="Sign Up", command=switch_to_signup, bg="#00C896", fg="white", font=("Arial", 12))
btn_signup.pack(side="left", expand=True, fill="both")

btn_login = tk.Button(tabs_frame, text="Log In", command=switch_to_login, bg="#444444", fg="white", font=("Arial", 12))
btn_login.pack(side="left", expand=True, fill="both")

# Signup Frame
signup_frame = tk.Frame(root, bg="#1E1E1E")

tk.Label(signup_frame, text="Sign Up for Free", fg="white", bg="#1E1E1E", font=("Arial", 14, "bold")).pack(pady=10)

entry_first_name = tk.Entry(signup_frame, width=30, bg="#333333", fg="white", insertbackground="white")
entry_first_name.pack(pady=5)
entry_first_name.insert(0, "First Name")

entry_last_name = tk.Entry(signup_frame, width=30, bg="#333333", fg="white", insertbackground="white")
entry_last_name.pack(pady=5)
entry_last_name.insert(0, "Last Name")

entry_email = tk.Entry(signup_frame, width=30, bg="#333333", fg="white", insertbackground="white")
entry_email.pack(pady=5)
entry_email.insert(0, "Email Address")

entry_password = tk.Entry(signup_frame, width=30, show="*", bg="#333333", fg="white", insertbackground="white")
entry_password.pack(pady=5)
entry_password.insert(0, "Set A Password")

tk.Button(signup_frame, text="GET STARTED", command=save_user, bg="#00C896", fg="white", font=("Arial", 14, "bold"), width=20).pack(pady=20)

# Login Frame
login_frame = tk.Frame(root, bg="#1E1E1E")

tk.Label(login_frame, text="Log In", fg="white", bg="#1E1E1E", font=("Arial", 14, "bold")).pack(pady=20)

login_email = tk.Entry(login_frame, width=30, bg="#333333", fg="white", insertbackground="white")
login_email.pack(pady=5)
login_email.insert(0, "Email Address")

login_password = tk.Entry(login_frame, width=30, show="*", bg="#333333", fg="white", insertbackground="white")
login_password.pack(pady=5)
login_password.insert(0, "Password")

tk.Button(login_frame, text="LOGIN", command=verify_login, bg="#00C896", fg="white", font=("Arial", 14, "bold"), width=20).pack(pady=20)

# Default to signup page
signup_frame.pack()

root.mainloop()
