# main_con_checkboxes.py - Sistema RRHH con Checkboxes Reales
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime
from config import *
from procesador import procesador

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.create_login_window()
    
    def create_login_window(self):
        # Crear ventana principal para login
        self.root = tk.Tk()
        self.root.title("Login - Sistema RRHH")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        self.root.configure(bg='white')
        
        # Centrar ventana
        self.root.eval('tk::PlaceWindow . center')
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='white', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Título
        title_label = tk.Label(
            main_frame, 
            text=TITULO_APP,
            font=('Arial', 18, 'bold'),
            bg='white',
            fg=COLOR_PRINCIPAL
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(
            main_frame, 
            text=f"{EMPRESA} - {VERSION}",
            font=('Arial', 12),
            bg='white',
            fg='gray'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Campos de login
        tk.Label(main_frame, text="Usuario:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        self.usuario_entry = tk.Entry(main_frame, font=('Arial', 12), width=25, relief='solid', bd=1)
        self.usuario_entry.pack(pady=(0, 15), ipady=8)
        
        tk.Label(main_frame, text="Contraseña:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        self.password_entry = tk.Entry(main_frame, show='*', font=('Arial', 12), width=25, relief='solid', bd=1)
        self.password_entry.pack(pady=(0, 20), ipady=8)
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=15)
        
        login_btn = tk.Button(
            btn_frame,
            text="🔐 Ingresar al Sistema",
            command=self.login,
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 11, 'bold'),
            width=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=self.root.quit,
            bg='#6c757d',
            fg='white',
            font=('Arial', 11),
            width=12,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_label = tk.Label(
            main_frame, 
            text="Ingrese sus credenciales de acceso",
            bg='white',
            fg='gray',
            font=('Arial', 10)
        )
        self.status_label.pack(pady=(20, 0))
        
        # Info de usuarios
        info_frame = tk.Frame(main_frame, bg='#f8f9fa', relief='solid', bd=1)
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(
            info_frame,
            text="👥 Usuarios disponibles:",
            bg='#f8f9fa',
            fg='#495057',
            font=('Arial', 9, 'bold')
        ).pack(pady=(8, 5))
        
        for user, pwd in USUARIOS_DEFAULT.items():
            tk.Label(
                info_frame,
                text=f"• {user} / {pwd}",
                bg='#f8f9fa',
                fg='#6c757d',
                font=('Arial', 9)
            ).pack()
        
        tk.Label(info_frame, text="", bg='#f8f9fa').pack(pady=2)  # Espaciado
        
        # Eventos
        self.usuario_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Focus inicial
        self.usuario_entry.focus()
        
        # Iniciar loop
        self.root.mainloop()
    
    def login(self):
        usuario = self.usuario_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not usuario or not password:
            self.status_label.config(text="⚠️ Complete todos los campos", fg=COLOR_ERROR)
            return
        
        self.status_label.config(text="🔄 Validando credenciales...", fg='blue')
        self.root.update()
        
        if procesador.validar_usuario(usuario, password):
            self.status_label.config(text="✅ Acceso autorizado", fg='green')
            self.root.update()
            self.root.after(500, lambda: self.success_login(usuario))
        else:
            self.status_label.config(text="❌ Usuario o contraseña incorrectos", fg=COLOR_ERROR)
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def success_login(self, usuario):
        self.root.destroy()
        self.on_login_success(usuario)

class SancionCheckbox:
    """Clase para manejar checkbox de cada sanción"""
    def __init__(self, sancion, parent_frame, row, on_selection_change):
        self.sancion = sancion
        self.parent_frame = parent_frame
        self.row = row
        self.on_selection_change = on_selection_change
        
        # Variable para el checkbox
        self.is_selected = tk.BooleanVar()
        self.is_selected.trace('w', self.on_check_change)
        
        self.create_row()
    
    def create_row(self):
        """Crear la fila con checkbox y datos"""
        # Frame para la fila completa
        self.row_frame = tk.Frame(self.parent_frame, bg='white', relief='solid', bd=1)
        self.row_frame.grid(row=self.row, column=0, sticky='ew', padx=2, pady=1)
        
        # Configurar grid
        self.row_frame.grid_columnconfigure(1, weight=1)  # Nombre empleado se expande
        self.row_frame.grid_columnconfigure(5, weight=1)  # Observaciones se expande
        
        # Color alternado
        bg_color = '#f8f9fa' if self.row % 2 == 0 else 'white'
        self.row_frame.configure(bg=bg_color)
        
        # Checkbox
        self.checkbox = tk.Checkbutton(
            self.row_frame,
            variable=self.is_selected,
            bg=bg_color,
            activebackground=bg_color,
            font=('Arial', 12),
            cursor='hand2'
        )
        self.checkbox.grid(row=0, column=0, padx=5, pady=5)
        
        # ID (primeros 8 caracteres)
        id_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('id', '')[:8] + '...',
            bg=bg_color,
            font=('Arial', 9),
            width=12,
            anchor='center'
        )
        id_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Código empleado
        cod_label = tk.Label(
            self.row_frame,
            text=str(self.sancion.get('empleado_cod', '')),
            bg=bg_color,
            font=('Arial', 9, 'bold'),
            width=8,
            anchor='center'
        )
        cod_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Nombre empleado
        nombre_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('empleado_nombre', ''),
            bg=bg_color,
            font=('Arial', 9),
            anchor='w',
            wraplength=200
        )
        nombre_label.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        # Tipo sanción
        tipo_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('tipo_sancion', ''),
            bg=bg_color,
            font=('Arial', 9, 'bold'),
            width=15,
            anchor='center',
            fg=COLOR_SECUNDARIO
        )
        tipo_label.grid(row=0, column=4, padx=5, pady=5)
        
        # Fecha
        fecha_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('fecha', '')[:10],
            bg=bg_color,
            font=('Arial', 9),
            width=12,
            anchor='center'
        )
        fecha_label.grid(row=0, column=5, padx=5, pady=5)
        
        # Observaciones (truncadas)
        obs_text = self.sancion.get('observaciones', '') or ''
        obs_display = (obs_text[:40] + '...') if len(obs_text) > 40 else obs_text
        obs_label = tk.Label(
            self.row_frame,
            text=obs_display,
            bg=bg_color,
            font=('Arial', 8),
            anchor='w',
            wraplength=250
        )
        obs_label.grid(row=0, column=6, padx=5, pady=5, sticky='w')
        
        # Botón detalles
        detalles_btn = tk.Button(
            self.row_frame,
            text="👁️",
            command=self.show_details,
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 8),
            width=3,
            height=1,
            relief='flat',
            cursor='hand2'
        )
        detalles_btn.grid(row=0, column=7, padx=5, pady=2)
        
        # Evento para seleccionar toda la fila
        for widget in [self.row_frame, id_label, cod_label, nombre_label, tipo_label, fecha_label, obs_label]:
            widget.bind('<Button-1>', self.toggle_selection)
    
    def on_check_change(self, *args):
        """Callback cuando cambia el estado del checkbox"""
        self.update_row_color()
        self.on_selection_change()
    
    def toggle_selection(self, event=None):
        """Alternar selección al hacer click en la fila"""
        self.is_selected.set(not self.is_selected.get())
    
    def update_row_color(self):
        """Actualizar color de la fila según selección"""
        if self.is_selected.get():
            # Seleccionada - color verde
            bg_color = '#d4edda'
        else:
            # No seleccionada - color alternado
            bg_color = '#f8f9fa' if self.row % 2 == 0 else 'white'
        
        # Aplicar color a todos los widgets de la fila
        self.row_frame.configure(bg=bg_color)
        for child in self.row_frame.winfo_children():
            if isinstance(child, (tk.Label, tk.Checkbutton)):
                child.configure(bg=bg_color, activebackground=bg_color)
    
    def show_details(self):
        """Mostrar detalles completos de la sanción"""
        details_window = tk.Toplevel()
        details_window.title(f"Detalles - {self.sancion.get('empleado_nombre', 'N/A')}")
        details_window.geometry("600x500")
        details_window.configure(bg='white')
        details_window.transient(self.row_frame.winfo_toplevel())
        details_window.grab_set()
        
        # Contenido
        text_widget = scrolledtext.ScrolledText(
            details_window, 
            wrap=tk.WORD, 
            font=('Courier', 10),
            bg='white',
            padx=15,
            pady=15
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Formatear información
        content = f"""
📋 DETALLES COMPLETOS DE LA SANCIÓN

🆔 ID: {self.sancion.get('id', 'N/A')}
👤 Empleado: {self.sancion.get('empleado_cod', 'N/A')} - {self.sancion.get('empleado_nombre', 'N/A')}
💼 Puesto: {self.sancion.get('puesto', 'N/A')}
👮 Agente: {self.sancion.get('agente', 'N/A')}
📅 Fecha: {self.sancion.get('fecha', 'N/A')}
🕐 Hora: {self.sancion.get('hora', 'N/A')}
⚠️ Tipo: {self.sancion.get('tipo_sancion', 'N/A')}
📝 Observaciones: {self.sancion.get('observaciones', 'N/A')}
📑 Obs. Adicionales: {self.sancion.get('observaciones_adicionales', 'N/A') or 'Ninguna'}
✅ Status: {self.sancion.get('status', 'N/A')}
💬 Comentarios Gerencia: {self.sancion.get('comentarios_gerencia', 'N/A') or 'Ninguno'}
🏢 Comentarios RRHH: {self.sancion.get('comentarios_rrhh', 'N/A') or 'PENDIENTE'}
📷 Foto URL: {self.sancion.get('foto_url', 'N/A') or 'No disponible'}
⏰ Creado: {self.sancion.get('created_at', 'N/A')}
🔄 Actualizado: {self.sancion.get('updated_at', 'N/A')}
        """
        
        text_widget.insert(tk.END, content.strip())
        text_widget.config(state=tk.DISABLED)
        
        # Botón cerrar
        close_btn = tk.Button(
            details_window,
            text="Cerrar",
            command=details_window.destroy,
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        )
        close_btn.pack(pady=10)

class SancionesTab:
    def __init__(self, parent, categoria, sanciones, on_procesar, on_refresh):
        self.categoria = categoria
        self.sanciones = sanciones
        self.on_procesar = on_procesar
        self.on_refresh = on_refresh
        self.checkboxes = []
        
        self.create_tab(parent)
    
    def create_tab(self, parent):
        # Frame principal
        main_frame = tk.Frame(parent, bg='white')
        
        # Header con info y estilo
        header_frame = tk.Frame(main_frame, bg=COLOR_PRINCIPAL, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
        
        # Título y contador
        title_frame = tk.Frame(header_frame, bg=COLOR_PRINCIPAL)
        title_frame.pack(expand=True, fill=tk.BOTH)
        
        header_label = tk.Label(
            title_frame,
            text=f"📋 {self.categoria}",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 16, 'bold')
        )
        header_label.pack(pady=(15, 5))
        
        count_label = tk.Label(
            title_frame,
            text=f"{len(self.sanciones)} sanciones pendientes",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 11)
        )
        count_label.pack()
        
        # Frame para controles
        controls_frame = tk.Frame(main_frame, bg='white')
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Lado izquierdo - Selección
        left_controls = tk.Frame(controls_frame, bg='white')
        left_controls.pack(side=tk.LEFT)
        
        select_all_btn = tk.Button(
            left_controls,
            text="☑️ Seleccionar Todo",
            command=self.select_all,
            bg=COLOR_SECUNDARIO,
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        )
        select_all_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        clear_btn = tk.Button(
            left_controls,
            text="🗑️ Limpiar Todo",
            command=self.clear_all,
            bg='#6c757d',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Contador de seleccionadas
        self.selected_count_label = tk.Label(
            left_controls,
            text="0 seleccionadas",
            bg='white',
            fg='gray',
            font=('Arial', 10, 'bold')
        )
        self.selected_count_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Lado derecho - Acciones
        right_controls = tk.Frame(controls_frame, bg='white')
        right_controls.pack(side=tk.RIGHT)
        
        refresh_btn = tk.Button(
            right_controls,
            text="🔄 Actualizar",
            command=self.on_refresh,
            bg='#17a2b8',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.process_btn = tk.Button(
            right_controls,
            text="⚡ Procesar Seleccionadas",
            command=self.procesar_seleccionadas,
            bg=COLOR_EXITO,
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.process_btn.pack(side=tk.RIGHT)
        
        # Header de la tabla
        header_table_frame = tk.Frame(main_frame, bg=COLOR_PRINCIPAL, height=35)
        header_table_frame.pack(fill=tk.X, pady=(0, 5))
        header_table_frame.pack_propagate(False)
        
        # Configurar grid del header
        header_table_frame.grid_columnconfigure(1, weight=1)
        header_table_frame.grid_columnconfigure(5, weight=1)
        
        headers = ['☑️', 'ID', 'Cód', 'Nombre Empleado', 'Tipo', 'Fecha', 'Observaciones', '👁️']
        widths = [50, 100, 60, 200, 120, 100, 250, 40]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = tk.Label(
                header_table_frame,
                text=header,
                bg=COLOR_PRINCIPAL,
                fg='white',
                font=('Arial', 10, 'bold'),
                width=width//8 if i not in [3, 6] else 0  # Ancho fijo excepto para nombre y observaciones
            )
            label.grid(row=0, column=i, padx=2, pady=5, sticky='ew' if i in [3, 6] else '')
        
        # Frame scrollable para las sanciones
        canvas_frame = tk.Frame(main_frame, relief='solid', bd=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Canvas y scrollbar
        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Pack canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para scroll con rueda del mouse
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Poblar con sanciones
        self.populate_sanciones()
        
        # Footer con información
        footer_frame = tk.Frame(main_frame, bg='#f8f9fa', height=40)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text=f"💡 Tip: Haz click en 👁️ para ver detalles completos | Click en la fila para seleccionar",
            bg='#f8f9fa',
            fg='#6c757d',
            font=('Arial', 9)
        )
        footer_label.pack(pady=10)
        
        # Actualizar contador inicial
        self.update_selected_count()
        
        return main_frame
    
    def populate_sanciones(self):
        """Crear checkboxes para cada sanción"""
        self.checkboxes = []
        
        for i, sancion in enumerate(self.sanciones):
            checkbox_row = SancionCheckbox(
                sancion, 
                self.scrollable_frame, 
                i, 
                self.update_selected_count
            )
            self.checkboxes.append(checkbox_row)
        
        # Actualizar región scrollable
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def select_all(self):
        """Seleccionar todas las sanciones"""
        for checkbox in self.checkboxes:
            checkbox.is_selected.set(True)
    
    def clear_all(self):
        """Deseleccionar todas las sanciones"""
        for checkbox in self.checkboxes:
            checkbox.is_selected.set(False)
    
    def update_selected_count(self):
        """Actualizar contador de seleccionadas"""
        count = sum(1 for cb in self.checkboxes if cb.is_selected.get())
        self.selected_count_label.config(text=f"{count} seleccionadas")
        
        # Habilitar/deshabilitar botón procesar
        if count > 0:
            self.process_btn.config(state='normal', bg=COLOR_EXITO)
        else:
            self.process_btn.config(state='disabled', bg='#6c757d')
    
    def procesar_seleccionadas(self):
        """Procesar sanciones seleccionadas"""
        sanciones_seleccionadas = [
            cb.sancion for cb in self.checkboxes 
            if cb.is_selected.get()
        ]
        
        if not sanciones_seleccionadas:
            messagebox.showwarning("Advertencia", "No hay sanciones seleccionadas")
            return
        
        self.on_procesar(sanciones_seleccionadas, self.categoria)

class MainWindow:
    def __init__(self, usuario):
        self.usuario = usuario
        self.sanciones_categorizadas = {}
        self.root = tk.Tk()
        
        self.setup_main_window()
        self.cargar_datos()
        self.root.mainloop()
    
    def setup_main_window(self):
        self.root.title(f"{TITULO_APP} - {self.usuario}")
        self.root.geometry("1400x800")
        self.root.configure(bg='white')
        
        # Maximizar ventana
        self.root.state('zoomed')  # Windows
        
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Sistema
        sistema_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🏠 Sistema", menu=sistema_menu)
        sistema_menu.add_command(label="🔄 Actualizar Datos", command=self.cargar_datos)
        sistema_menu.add_command(label="📊 Estadísticas", command=self.mostrar_estadisticas)
        sistema_menu.add_separator()
        sistema_menu.add_command(label="❌ Salir", command=self.root.quit)
        
        # Menu Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 Herramientas", menu=tools_menu)
        tools_menu.add_command(label="🧪 Crear Sanción Prueba", command=self.crear_sancion_prueba)
        tools_menu.add_command(label="🔍 Test Conexión", command=self.test_conexion)
        
        # Header principal
        header_frame = tk.Frame(self.root, bg=COLOR_PRINCIPAL, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header_frame, bg=COLOR_PRINCIPAL)
        header_content.pack(expand=True, fill=tk.BOTH, padx=20)
        
        # Título principal
        title_label = tk.Label(
            header_content,
            text=f"🏢 {TITULO_APP}",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 20, 'bold')
        )
        title_label.pack(side=tk.LEFT, pady=20)
        
        # Info usuario y status
        user_frame = tk.Frame(header_content, bg=COLOR_PRINCIPAL)
        user_frame.pack(side=tk.RIGHT, pady=20)
        
        user_label = tk.Label(
            user_frame,
            text=f"👤 Usuario: {self.usuario}",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 12, 'bold')
        )
        user_label.pack(anchor='e')
        
        self.status_label = tk.Label(
            user_frame,
            text="🔄 Cargando sistema...",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 10)
        )
        self.status_label.pack(anchor='e')
        
        # Notebook para pestañas con estilo
        style = ttk.Style()
        style.configure('Custom.TNotebook', background='white')
        style.configure('Custom.TNotebook.Tab', 
                       padding=[20, 10], 
                       font=('Arial', 11, 'bold'))
        
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#f8f9fa', height=40)
        footer_frame.pack(fill=tk.X)
        footer_frame.pack_propagate(False)
        
        footer_content = tk.Frame(footer_frame, bg='#f8f9fa')
        footer_content.pack(expand=True, fill=tk.BOTH, padx=20)
        
        footer_left = tk.Label(
            footer_content,
            text=f"© {datetime.now().year} {EMPRESA} - {VERSION}",
            bg='#f8f9fa',
            fg='#6c757d',
            font=('Arial', 9)
        )
        footer_left.pack(side=tk.LEFT, pady=10)
        
        self.footer_right = tk.Label(
            footer_content,
            text=f"🕐 Última actualización: {datetime.now().strftime('%H:%M:%S')}",
            bg='#f8f9fa',
            fg='#6c757d',
            font=('Arial', 9)
        )
        self.footer_right.pack(side=tk.RIGHT, pady=10)
    
    def cargar_datos(self):
        self.status_label.config(text="🔄 Cargando sanciones...")
        self.footer_right.config(text="🔄 Actualizando datos...")
        self.root.update()
        
        # Cargar en hilo separado
        thread = threading.Thread(target=self._cargar_datos_thread)
        thread.daemon = True
        thread.start()
    
    def _cargar_datos_thread(self):
        try:
            # Test conexión
            if not procesador.test_conexion_supabase():
                self.root.after(0, lambda: self.status_label.config(text="❌ Sin conexión"))
                self.root.after(0, lambda: messagebox.showerror("Error", MSG_CONEXION_ERROR))
                return
            
            # Obtener sanciones
            sanciones = procesador.obtener_sanciones_pendientes()
            self.sanciones_categorizadas = procesador.categorizar_sanciones(sanciones)
            
            # Actualizar UI en hilo principal
            self.root.after(0, self._actualizar_pestañas)
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="❌ Error cargando"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error cargando datos: {e}"))
    
    def _actualizar_pestañas(self):
        # Limpiar pestañas existentes
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Crear pestañas para cada categoría
        for categoria, sanciones in self.sanciones_categorizadas.items():
            tab_obj = SancionesTab(
                self.notebook, 
                categoria, 
                sanciones, 
                self.procesar_sanciones,
                self.cargar_datos
            )
            tab_frame = tab_obj.create_tab(self.notebook)
            
            # Emoji por categoría
            emoji = {
                "Faltas y Permisos": "📋",
                "Horas y Franco": "⏰", 
                "Resto": "⚠️"
            }.get(categoria, "📄")
            
            self.notebook.add(tab_frame, text=f"{emoji} {categoria} ({len(sanciones)})")
        
        total_sanciones = sum(len(s) for s in self.sanciones_categorizadas.values())
        self.status_label.config(text=f"✅ {total_sanciones} sanciones pendientes")
        self.footer_right.config(text=f"🕐 Actualizado: {datetime.now().strftime('%H:%M:%S')}")
    
    def procesar_sanciones(self, sanciones, categoria):
        if not sanciones:
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Procesamiento",
            f"¿Procesar {len(sanciones)} sanciones de '{categoria}'?\n\n"
            f"Esto actualizará el campo 'comentarios_rrhh' en Supabase.\n\n"
            f"¿Desea continuar?"
        )
        
        if not respuesta:
            return
        
        # Mostrar progreso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Procesando Sanciones")
        progress_window.geometry("450x200")
        progress_window.configure(bg='white')
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_frame = tk.Frame(progress_window, bg='white', padx=30, pady=30)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            progress_frame, 
            text="⚡ Procesando sanciones...", 
            bg='white',
            font=('Arial', 14, 'bold'),
            fg=COLOR_PRINCIPAL
        ).pack(pady=(0, 20))
        
        progress = ttk.Progressbar(progress_frame, length=350, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        status_lbl = tk.Label(
            progress_frame, 
            text="Iniciando procesamiento...", 
            bg='white',
            font=('Arial', 10),
            fg='#6c757d'
        )
        status_lbl.pack(pady=10)
        
        # Procesar en hilo separado
        thread = threading.Thread(
            target=self._procesar_thread,
            args=(sanciones, progress_window, status_lbl, progress)
        )
        thread.daemon = True
        thread.start()
    
    def _procesar_thread(self, sanciones, progress_window, status_lbl, progress):
        try:
            exitosas, fallidas = procesador.procesar_multiples_sanciones(sanciones, self.usuario)
            
            # Cerrar ventana de progreso
            self.root.after(0, progress_window.destroy)
            
            # Mostrar resultado
            if exitosas > 0:
                mensaje = f"✅ Procesamiento completado exitosamente\n\n"
                mensaje += f"🎯 Sanciones procesadas: {exitosas}\n"
                if fallidas > 0:
                    mensaje += f"❌ Sanciones fallidas: {fallidas}\n"
                mensaje += f"\n✨ Las sanciones han sido marcadas en Supabase"
                
                self.root.after(0, lambda: messagebox.showinfo("Éxito", mensaje))
                self.root.after(0, self.cargar_datos)  # Recargar datos
            else:
                mensaje = f"❌ No se pudieron procesar las sanciones\n\n"
                mensaje += f"Fallidas: {fallidas}\n"
                mensaje += f"Verifique la conexión y permisos"
                
                self.root.after(0, lambda: messagebox.showerror("Error", mensaje))
                
        except Exception as e:
            self.root.after(0, progress_window.destroy)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error procesando: {e}"))
    
    def mostrar_estadisticas(self):
        stats = procesador.obtener_estadisticas()
        
        if not stats:
            messagebox.showwarning("Advertencia", "No se pudieron obtener estadísticas")
            return
        
        # Ventana de estadísticas
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Estadísticas del Sistema")
        stats_window.geometry("600x500")
        stats_window.configure(bg='white')
        stats_window.transient(self.root)
        
        # Contenido
        text_widget = scrolledtext.ScrolledText(
            stats_window, 
            wrap=tk.WORD, 
            font=('Courier', 11),
            bg='white',
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        contenido = f"""
📊 ESTADÍSTICAS DEL SISTEMA RRHH
{"="*50}

📈 RESUMEN GENERAL:
• Total procesadas: {stats.get('total_procesadas', 0)}
• Procesadas hoy: {stats.get('procesadas_hoy', 0)}

👤 POR USUARIO:
{"─"*30}
"""
        
        for usuario, cantidad in stats.get('por_usuario', {}).items():
            contenido += f"• {usuario}: {cantidad} sanciones\n"
        
        contenido += f"\n🏷️ POR TIPO DE SANCIÓN:\n{'─'*30}\n"
        for tipo, cantidad in stats.get('por_tipo', {}).items():
            contenido += f"• {tipo}: {cantidad}\n"
        
        contenido += f"""

📅 INFORMACIÓN DE SESIÓN:
{"─"*30}
• Usuario actual: {self.usuario}
• Fecha: {datetime.now().strftime('%Y-%m-%d')}
• Hora: {datetime.now().strftime('%H:%M:%S')}
• Sistema: {TITULO_APP} {VERSION}

🔗 CONEXIÓN:
{"─"*30}
• Base remota: Supabase
• Base local: SQLite
• Estado: ✅ Conectado
        """
        
        text_widget.insert(tk.END, contenido)
        text_widget.config(state=tk.DISABLED)
    
    def crear_sancion_prueba(self):
        if procesador.crear_sancion_prueba():
            messagebox.showinfo("Éxito", "✅ Sanción de prueba creada exitosamente")
            self.cargar_datos()
        else:
            messagebox.showerror("Error", "❌ No se pudo crear la sanción de prueba")
    
    def test_conexion(self):
        if procesador.test_conexion_supabase():
            messagebox.showinfo("Conexión", "✅ Conexión con Supabase exitosa")
        else:
            messagebox.showerror("Conexión", "❌ Error de conexión con Supabase")

def main():
    print("🚀 Iniciando Sistema RRHH con Checkboxes Reales...")
    
    def on_login_success(usuario):
        app = MainWindow(usuario)
    
    # Mostrar login
    login = LoginWindow(on_login_success)

if __name__ == "__main__":
    main()
