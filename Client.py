import sqlite3
from tkinter import messagebox
import customtkinter as ctk

# Initialize and setup the SQLite database
with sqlite3.connect("helpdesk.db") as conn:
  conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT, 
            title TEXT, 
            category TEXT, 
            priority TEXT, 
            description TEXT, 
            status TEXT
        )
    """)

# Configure theming to match the operating system
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# runs the main client window
app = ctk.CTk()
app.title("Client Portal")
app.geometry("440x580")
app.resizable(True, True)

# App Title
ctk.CTkLabel(
    app, text="IT Support Ticket Submittion Portal", font=ctk.CTkFont(size=20, weight="bold")
).pack(anchor="center", padx=25, pady=(20, 10))

# Forms container card
card = ctk.CTkFrame(app, corner_radius=12)
card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

# Helper function to create consistent form field labels
def add_lbl(text):  
  ctk.CTkLabel(card, text=text, font=ctk.CTkFont(size=11, weight="bold")).pack(
      anchor="w", padx=15, pady=(8, 2)
  )


# Ticket Form Input Fields
add_lbl("Email Address")
email_e = ctk.CTkEntry(card, placeholder_text="name@company.com", height=34)
email_e.pack(fill="x", padx=15)

add_lbl("Issue Title")
title_e = ctk.CTkEntry(card, placeholder_text="Brief summary", height=34)
title_e.pack(fill="x", padx=15)

add_lbl("Category")
cat_cb = ctk.CTkComboBox(
    card,
    values=["Hardware", "Software", "Network / Wi-Fi", "Access / Password", "Other"],
    height=34,
    state="readonly",
)
cat_cb.pack(fill="x", padx=15)
cat_cb.set("Hardware")

add_lbl("Priority")
pri_cb = ctk.CTkComboBox(
    card, values=["Low", "Medium", "High", "Urgent"], height=34, state="readonly"
)
pri_cb.pack(fill="x", padx=15)
pri_cb.set("Low")

add_lbl("Description")
desc_t = ctk.CTkTextbox(card, height=70, corner_radius=6)
desc_t.pack(fill="x", padx=15, pady=(0, 10))

# Validates inputs, saves the ticket record to the database, and resets form.
def submit_ticket():
  email = email_e.get().strip()
  title = title_e.get().strip()
  desc = desc_t.get("1.0", "end-1c").strip()

  # Input validation for empty fields and email format
  if not email or not title or not desc:
    return messagebox.showerror("Error", "Please fill in all fields.")
  if "@" not in email or "." not in email:
    return messagebox.showerror("Error", "Enter a valid email address.")

  # Insert ticket record into database with an initial status of 'Open'
  with sqlite3.connect("helpdesk.db") as conn:
    conn.execute(
        "INSERT INTO tickets (email, title, category, priority, description, status) VALUES (?, ?, ?, ?, ?, ?)",
        (email, title, cat_cb.get(), pri_cb.get(), desc, "Open"),
    )

  # Clear inputs and show confirmation
  email_e.delete(0, "end")
  title_e.delete(0, "end")
  desc_t.delete("1.0", "end")
  cat_cb.set("Hardware")
  pri_cb.set("Low")
  messagebox.showinfo("Success", "Ticket submitted successfully!")


# Submit Button
ctk.CTkButton(
    card,
    text="Submit Ticket",
    height=36,
    fg_color="#2563eb",
    hover_color="#1d4ed8",
    command=submit_ticket,
).pack(fill="x", padx=15, pady=(0, 15))

app.mainloop()