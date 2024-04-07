import sqlite3
from datetime import datetime

def crea_tabella_scommesse():
    conn = sqlite3.connect('scommesse.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scommesse
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, importo REAL, vincita_reale REAL, risultato TEXT, data TEXT, differenza REAL)''')
    conn.commit()
    conn.close()

def inserisci_scommessa(importo, risultato, data):
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

def mostra_storico():
    conn = sqlite3.connect('scommesse.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM scommesse''')
    storico = c.fetchall()
    conn.close()
    return storico

def main():
    crea_tabella_scommesse()
    
    while True:
        print("\nGestione scommesse sportive:")
        print("1. Inserisci una scommessa")
        print("2. Mostra storico delle scommesse")
        print("3. Esci")

        scelta = input("Scegli un'opzione: ")

        if scelta == '1':
            importo = float(input("Inserisci l'importo della scommessa: "))
            risultato = input("Inserisci il risultato della scommessa (vincita/perdita): ").lower()
            data = datetime.now().strftime('%d-%m-%Y')  # Utilizzo la data attuale nel formato italiano
            inserisci_scommessa(importo, risultato, data)
            print("Scommessa registrata.")
        elif scelta == '2':
            storico = mostra_storico()
            if storico:
                for scommessa in storico:
                    saldo_giornaliero = calcola_saldo_giornaliero(scommessa[4])  # La data è nella quinta colonna
                    saldo_totale = calcola_saldo_totale()
                    print(f"ID: {scommessa[0]}, Importo: {scommessa[1]}, Vincita reale: {scommessa[2]}, Risultato: {scommessa[3]}, Data: {scommessa[4]}, Saldo giornaliero: {saldo_giornaliero}, Saldo totale: {saldo_totale}")
            else:
                print("Nessuna scommessa effettuata.")
        elif scelta == '3':
            print("Grazie per aver utilizzato l'applicazione. Arrivederci!")
            break
        else:
            print("Opzione non valida. Riprova.")


if __name__ == "__main__":
    main()
