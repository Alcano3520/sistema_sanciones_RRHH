# test_tk.py - Prueba simple de tkinter
import tkinter as tk

def test_tkinter():
    print("🔧 Probando tkinter...")
    
    # Crear ventana simple
    root = tk.Tk()
    root.title("Prueba Tkinter")
    root.geometry("300x200")
    
    # Agregar texto
    label = tk.Label(root, text="✅ Tkinter funciona!", font=('Arial', 14))
    label.pack(pady=50)
    
    # Botón para cerrar
    btn = tk.Button(root, text="Cerrar", command=root.quit)
    btn.pack(pady=10)
    
    print("🔧 Iniciando ventana tkinter...")
    root.mainloop()
    print("🔧 Ventana cerrada")

if __name__ == "__main__":
    test_tkinter()
