import sqlite3
from tkinter import messagebox, ttk
import customtkinter as ctk

# Configure global theme settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Initialize admin dashboard window
app = ctk.CTk()
app.title("Admin Dashboard")
app.geometry("960x500")
app.resizable(True, True)


# Queries the database to retrieve the highest ticket ID.
def get_max_id():
  try:
    with sqlite3.connect("helpdesk.db") as conn:
      return conn.execute("SELECT MAX(id) FROM tickets").fetchone()[0] or 0
  except:
    return 0


# Track the current highest ticket ID for change detection
last_max_id = get_max_id()


# Clears and re-populates the treeview table with records from the database.
def load_tickets():
  tree.delete(*tree.get_children())
  with sqlite3.connect("helpdesk.db") as conn:
    for row in conn.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall():
      tree.insert("", "end", values=row)


# Background polling loop executed every 5 seconds to detect new database records.
def poll_loop():
  global last_max_id
  curr_max = get_max_id()

  if curr_max > last_max_id:
    last_max_id = curr_max
    load_tickets()
    app.bell()
    messagebox.showinfo(
        "New Ticket Alert", "A new support ticket has been received!"
    )

  app.after(5000, poll_loop)


# Returns the ID of the currently selected row in the table.
def get_selected_id():
  sel = tree.selection()
  if not sel:
    messagebox.showwarning("Warning", "Please select a ticket first.")
    return None
  return tree.item(sel)["values"][0]


# Updates the selected ticket's status to 'Resolved'.
def resolve_ticket():
  global last_max_id
  tid = get_selected_id()
  if tid:
    with sqlite3.connect("helpdesk.db") as conn:
      conn.execute("UPDATE tickets SET status = 'Resolved' WHERE id = ?", (tid,))
    load_tickets()
    last_max_id = get_max_id()


# Deletes the selected ticket from the database after user confirmation.
def delete_ticket():
  global last_max_id
  tid = get_selected_id()
  if tid and messagebox.askyesno("Confirm", f"Delete ticket #{tid}?"):
    with sqlite3.connect("helpdesk.db") as conn:
      conn.execute("DELETE FROM tickets WHERE id = ?", (tid,))
    load_tickets()
    last_max_id = get_max_id()


# Table UI Styling
# Configure custom styles for ttk Treeview to integrate with CustomTkinter dark mode
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 9, "bold"),
    background="#1e293b",
    foreground="white",
    relief="flat",
)
style.configure(
    "Treeview",
    rowheight=30,
    font=("Segoe UI", 9),
    background="#0f172a",
    fieldbackground="#0f172a",
    foreground="#f8fafc",
)
style.map(
    "Treeview",
    background=[("selected", "#2563eb")],
    foreground=[("selected", "white")],
)

# Header Frame
header = ctk.CTkFrame(app, fg_color="transparent")
header.pack(fill="x", padx=20, pady=15)
ctk.CTkLabel(
    header, text="Admin Dashboard", font=ctk.CTkFont(size=18, weight="bold")
).pack(side="left")

# Table Container Frame
tf = ctk.CTkFrame(app, corner_radius=8)
tf.pack(fill="both", expand=True, padx=20, pady=(0, 10))

cols = ("ID", "Email", "Title", "Category", "Priority", "Description", "Status")
tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")

widths = {
    "ID": 35,
    "Email": 150,
    "Title": 140,
    "Category": 110,
    "Priority": 75,
    "Description": 190,
    "Status": 75,
}

for c in cols:
  tree.heading(c, text=c)
  tree.column(
      c,
      width=widths.get(c, 100),
      anchor="center" if c in ("ID", "Priority", "Status") else "w",
  )

scrollbar = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)
scrollbar.pack(side="right", fill="y", pady=4)

# Actions Toolbar
af = ctk.CTkFrame(app, fg_color="transparent")
af.pack(fill="x", padx=20, pady=(0, 15))

ctk.CTkButton(
    af,
    text="Mark Resolved",
    fg_color="#0d9488",
    hover_color="#0f766e",
    height=34,
    command=resolve_ticket,
).pack(side="left", padx=(0, 10))

ctk.CTkButton(
    af,
    text="Delete",
    fg_color="#e11d48",
    hover_color="#be123c",
    height=34,
    command=delete_ticket,
).pack(side="left")

ctk.CTkButton(
    header, text="🔄 Refresh", width=90, height=30, command=load_tickets
).pack(side="right")

# Initialize data loading and start the background polling thread
load_tickets()
poll_loop()
app.mainloop()