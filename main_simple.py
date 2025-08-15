# main_simple.py - Versión simplificada para debug
import tkinter as tk
from tkinter import messagebox
from config import *
from procesador import procesador

def login_simple():
    """Login simplificado en una sola ventana"""
    
    def validar_login():
        usuario = entry_usuario.get().strip()
        password = entry_password.get().strip()
        
        print(f"🔍 Intentando login: {usuario}")
        
        if procesador.validar_usuario(usuario, password):
            print("✅ Login exitoso")
            label_status.config(text="✅ Login exitoso", fg="green")
            root.after(1000, lambda: abrir_sistema_principal(usuario))
        else:
            print("❌ Login fallido")
            label_status.config(text="❌ Usuario o contraseña incorrectos", fg="red")
            entry_password.delete(0, tk.END)
    
    def abrir_sistema_principal(usuario):
        """Abrir sistema principal simplificado"""
        root.destroy()
        
        # Ventana principal simple
        main_window = tk.Tk()
        main_window.title(f"Sistema RRHH - {usuario}")
        main_window.geometry("800x600")
        
        # Header
        frame_header = tk.Frame(main_window, bg=COLOR_PRINCIPAL, height=60)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)
        
        label_titulo = tk.Label(
            frame_header,
            text=f"Sistema RRHH - Usuario: {usuario}",
            bg=COLOR_PRINCIPAL,
            fg="white",
            font=('Arial', 14, 'bold')
        )
        label_titulo.pack(pady=15)
        
        # Contenido
        frame_contenido = tk.Frame(main_window)
        frame_contenido.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            frame_contenido,
            text="🎉 ¡Sistema funcionando!",
            font=('Arial', 16, 'bold')
        ).pack(pady=20)
        
        # Botón para cargar sanciones
        def cargar_sanciones():
            label_status_main.config(text="Cargando sanciones...")
            main_window.update()
            
            try:
                if not procesador.test_conexion_supabase():
                    label_status_main.config(text="❌ Error de conexión con Supabase")
                    return
                
                sanciones = procesador.obtener_sanciones_pendientes()
                categorizadas = procesador.categorizar_sanciones(sanciones)
                
                total = sum(len(s) for s in categorizadas.values())
                
                resultado = f"✅ Sanciones cargadas:\n"
                for categoria, lista in categorizadas.items():
                    resultado += f"• {categoria}: {len(lista)}\n"
                resultado += f"\nTotal: {total} sanciones pendientes"
                
                text_resultados.delete(1.0, tk.END)
                text_resultados.insert(tk.END, resultado)
                
                label_status_main.config(text=f"✅ {total} sanciones cargadas")
                
            except Exception as e:
                label_status_main.config(text=f"❌ Error: {e}")
                print(f"Error cargando sanciones: {e}")
        
        btn_cargar = tk.Button(
            frame_contenido,
            text="🔄 Cargar Sanciones Pendientes",
            command=cargar_sanciones,
            bg=COLOR_EXITO,
            fg="white",
            font=('Arial', 12, 'bold'),
            pady=10
        )
        btn_cargar.pack(pady=10)
        
        # Área de resultados
        text_resultados = tk.Text(
            frame_contenido,
            height=15,
            font=('Courier', 10)
        )
        text_resultados.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Status
        label_status_main = tk.Label(
            main_window,
            text="Listo para cargar sanciones",
            bg="lightgray",
            pady=5
        )
        label_status_main.pack(fill=tk.X)
        
        main_window.mainloop()
    
    # Crear ventana de login
    print("🔧 Creando ventana de login...")
    
    root = tk.Tk()
    root.title("Login - Sistema RRHH")
    root.geometry("400x300")
    root.resizable(False, False)
    
    # Contenido del login
    frame_main = tk.Frame(root, padx=40, pady=40)
    frame_main.pack(fill=tk.BOTH, expand=True)
    
    # Título
    tk.Label(
        frame_main,
        text=TITULO_APP,
        font=('Arial', 16, 'bold'),
        fg=COLOR_PRINCIPAL
    ).pack(pady=(0, 20))
    
    # Usuario
    tk.Label(frame_main, text="Usuario:", font=('Arial', 10)).pack(anchor='w')
    entry_usuario = tk.Entry(frame_main, font=('Arial', 11), width=25)
    entry_usuario.pack(pady=(5, 15), ipady=5)
    
    # Contraseña
    tk.Label(frame_main, text="Contraseña:", font=('Arial', 10)).pack(anchor='w')
    entry_password = tk.Entry(frame_main, show='*', font=('Arial', 11), width=25)
    entry_password.pack(pady=(5, 20), ipady=5)
    
    # Botón
    btn_login = tk.Button(
        frame_main,
        text="Ingresar",
        command=validar_login,
        bg=COLOR_PRINCIPAL,
        fg='white',
        font=('Arial', 10, 'bold'),
        width=15,
        pady=8
    )
    btn_login.pack(pady=10)
    
    # Status
    label_status = tk.Label(
        frame_main,
        text="Ingrese sus credenciales",
        font=('Arial', 9),
        fg='gray'
    )
    label_status.pack(pady=(10, 0))
    
    # Info de usuarios
    info_text = """
Usuarios por defecto:
• admin / 123456
• rrhh / rrhh2025
• supervisor / super123
    """
    tk.Label(
        frame_main,
        text=info_text,
        font=('Arial', 8),
        fg='blue',
        justify=tk.LEFT
    ).pack(pady=(20, 0))
    
    # Eventos
    entry_usuario.bind('<Return>', lambda e: entry_password.focus())
    entry_password.bind('<Return>', lambda e: validar_login())
    
    print("🔧 Iniciando ventana de login...")
    entry_usuario.focus()
    root.mainloop()

if __name__ == "__main__":
    print("🚀 Iniciando sistema RRHH simplificado...")
    login_simple()
