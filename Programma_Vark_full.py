import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from ttkthemes import ThemedTk

class ApplicazioneScommesse(ThemedTk):
    def __init__(self):
        super().__init__()
        self.set_theme("breeze")  # Scegliamo uno stile tematico per la finestra
        self.title("Gestione Scommesse Sportive")
        self.geometry("800x500")

        self.crea_interfaccia()
        self.crea_tabella_scommesse()

    def crea_interfaccia(self):
        self.lbl_benvenuto = ttk.Label(self, text="Benvenuto!", font=("Helvetica", 18))
        self.lbl_benvenuto.pack(pady=10)

        self.btn_inserisci_scommessa = ttk.Button(self, text="Inserisci una scommessa", command=self.inserisci_scommessa)
        self.btn_inserisci_scommessa.pack(pady=5)

        self.btn_mostra_storico = ttk.Button(self, text="Mostra storico delle scommesse", command=self.mostra_storico)
        self.btn_mostra_storico.pack(pady=5)

        self.btn_esci = ttk.Button(self, text="Esci", command=self.quit)
        self.btn_esci.pack(pady=5)

    def crea_tabella_scommesse(self):
        conn = sqlite3.connect('scommesse.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS scommesse
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, importo REAL, vincita_reale REAL, risultato TEXT, data TEXT, differenza REAL)''')
        conn.commit()
        conn.close()

    def inserisci_scommessa(self):
        # Creiamo una finestra per l'inserimento della scommessa
        inserimento_window = tk.Toplevel(self)
        inserimento_window.title("Inserisci Scommessa")

        lbl_importo = ttk.Label(inserimento_window, text="Importo:")
        lbl_importo.grid(row=0, column=0, padx=5, pady=5)
        entry_importo = ttk.Entry(inserimento_window)
        entry_importo.grid(row=0, column=1, padx=5, pady=5)

        lbl_risultato = ttk.Label(inserimento_window, text="Risultato (vincita/perdita):")
        lbl_risultato.grid(row=1, column=0, padx=5, pady=5)
        entry_risultato = ttk.Entry(inserimento_window)
        entry_risultato.grid(row=1, column=1, padx=5, pady=5)

        btn_conferma = ttk.Button(inserimento_window, text="Conferma", command=lambda: self.conferma_scommessa(inserimento_window, entry_importo.get(), entry_risultato.get()))
        btn_conferma.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def conferma_scommessa(self, inserimento_window, importo, risultato):
        inserimento_window.destroy()  # Chiudiamo la finestra di inserimento
        try:
            importo = float(importo)
        except ValueError:
            messagebox.showerror("Errore", "L'importo deve essere un numero.")
            return

        if risultato.lower() not in ['vincita', 'perdita']:
            messagebox.showerror("Errore", "Il risultato deve essere 'vincita' o 'perdita'.")
            return

        # Otteniamo la data attuale
        data = datetime.now().strftime('%d-%m-%Y')

        # Eseguiamo l'inserimento della scommessa nel database
        conn = sqlite3.connect('scommesse.db')
        c = conn.cursor()
        if risultato == 'vincita':
            vincita_reale = float(input("Inserisci l'importo della vincita reale: "))
            differenza = vincita_reale - importo
        else:
            vincita_reale = 0
            differenza = 0
        c.execute('''INSERT INTO scommesse (importo, vincita_reale, risultato, data, differenza) VALUES (?, ?, ?, ?, ?)''', (importo, vincita_reale, risultato, data, differenza))
        conn.commit()
        conn.close()

        messagebox.showinfo("Successo", "Scommessa registrata.")

    def mostra_storico(self):
        conn = sqlite3.connect('scommesse.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM scommesse''')
        storico = c.fetchall()
        conn.close()

        if storico:
            saldo_giornaliero = 0
            saldo_totale = 200  # Budget iniziale di 200 euro
            storico_window = tk.Toplevel(self)
            storico_window.title("Storico delle scommesse")
            tree = ttk.Treeview(storico_window)
            tree["columns"] = ("ID", "Importo", "Vincita reale", "Risultato", "Data", "Saldo giornaliero", "Saldo totale")
            tree.heading("#0", text="")
            tree.column("#0", minwidth=0, width=0, stretch=tk.NO)
            for col in tree["columns"]:
                tree.heading(col, text=col)
            for scommessa in storico:
                saldo_giornaliero = calcola_saldo_giornaliero(scommessa[4])  # La data è nella quinta colonna
                saldo_totale = calcola_saldo_totale()
                tree.insert("", "end", text="", values=(scommessa[0], scommessa[1], scommessa[2], scommessa[3], scommessa[4], saldo_giornaliero, saldo_totale))
            tree.pack(fill="both", expand=True)
        else:
            messagebox.showinfo("Storico delle scommesse", "Nessuna scommessa effettuata.")

def calcola_saldo_giornaliero(data):
    conn = sqlite3.connect('scommesse.db')
    c = conn.cursor()
    c.execute('''SELECT SUM(CASE WHEN risultato = 'vincita' THEN differenza ELSE -importo END) FROM scommesse WHERE data = ?''', (data,))
    saldo_giornaliero = c.fetchone()[0]
    conn.close()
    return "{:.2f}".format(saldo_giornaliero) if saldo_giornaliero is not None else 0

def calcola_saldo_totale():
    conn = sqlite3.connect('scommesse.db')
    c = conn.cursor()
    c.execute('''SELECT SUM(CASE WHEN risultato = 'vincita' THEN differenza ELSE -importo END) FROM scommesse''')
    saldo_totale = c.fetchone()[0]
    conn.close()
    saldo_totale += 200  # Aggiungiamo il budget iniziale di 200 euro
    return "{:.2f}".format(saldo_totale) if saldo_totale is not None else 0

if __name__ == "__main__":
    app = ApplicazioneScommesse()
    app.mainloop()
